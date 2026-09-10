from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from ui.runtime import (
    PROJECT_ROOT,
    account_rows,
    database_counts,
    job_rows,
    process_status,
    read_log,
    safe_name,
    start_process,
    stop_process,
)
from x_research.campaign import generate_experiment, load_campaign_config, plan_metrics
from x_research.storage import ResearchStore

st.set_page_config(
    page_title="X Research Console",
    page_icon="🔎",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1320px; padding-top: 2rem;}
      div[data-testid="stMetric"] {background:#111C2F; border:1px solid #24344F;
        padding:16px; border-radius:14px;}
      .small-note {color:#9FB0C8; font-size:.92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def campaign_files() -> list[Path]:
    paths = list((PROJECT_ROOT / "config").glob("*.json"))
    paths.extend((PROJECT_ROOT / "config" / "generated").glob("*.json"))
    valid: list[Path] = []
    for path in sorted(paths):
        try:
            load_campaign_config(path)
        except (ValueError, json.JSONDecodeError):
            continue
        valid.append(path)
    return valid


def paths_for(campaign_id: str) -> dict[str, Path]:
    root = PROJECT_ROOT / "data" / "runs" / safe_name(campaign_id)
    return {
        "root": root,
        "database": root / "research.sqlite3",
        "raw": root / "raw",
        "plan": root / "plan.json",
        "tweets_csv": root / "exports" / "tweets.csv",
        "threads_csv": root / "exports" / "threads.csv",
    }


def render_accounts() -> None:
    rows = account_rows(PROJECT_ROOT / "data" / "accounts.db")
    if not rows:
        st.warning("No se encontraron cuentas. Agregalas desde la Terminal siguiendo el README.")
        return
    table = pd.DataFrame(rows)
    table["estado"] = table["active"].map({1: "Activa", 0: "Inactiva"})
    st.dataframe(
        table[["username", "estado", "last_used", "error_msg"]],
        hide_index=True,
        width="stretch",
    )


def render_builder() -> None:
    st.subheader("Crear una campaña")
    st.caption(
        "La fecha final se interpreta como inclusiva en la pantalla "
        "y se guarda como límite exacto."
    )
    left, right = st.columns(2)
    with left:
        title = st.text_input("Identificador", "mi_campania")
        start = st.date_input("Primer día", date(2026, 7, 6))
    with right:
        end = st.date_input("Último día incluido", date(2026, 7, 10))
        window = st.selectbox(
            "Tamaño inicial de cada trabajo",
            options=[1440, 360, 60, 30, 15],
            format_func=lambda value: "1 día" if value == 1440 else f"{value} minutos",
        )

    limit = st.number_input("Máximo por trabajo", 20, 10000, 3000, 20)
    initial = pd.DataFrame(
        [
            {
                "etiqueta": "paraguas",
                "capa": "core",
                "consulta": '(Albiceleste OR Scaloneta OR "Selección argentina" OR AFA)',
            }
        ]
    )
    queries = st.data_editor(
        initial,
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "capa": st.column_config.SelectboxColumn(options=["core", "thematic"]),
            "consulta": st.column_config.TextColumn(width="large"),
        },
    )
    if st.button("Guardar campaña", type="primary"):
        if end < start:
            st.error("El último día no puede ser anterior al primero.")
            return
        records = []
        for row in queries.to_dict("records"):
            label = str(row.get("etiqueta", "")).strip()
            text = str(row.get("consulta", "")).strip()
            if label and text:
                records.append(
                    {
                        "label": safe_name(label),
                        "text": text,
                        "corpus_layer": row.get("capa") or "core",
                    }
                )
        if not records:
            st.error("Agregá al menos una consulta válida.")
            return
        campaign_id = safe_name(title)
        payload = {
            "campaign_id": campaign_id,
            "description": "Campaña creada desde la interfaz local.",
            "timezone": "America/Argentina/Buenos_Aires",
            "since": start.isoformat(),
            "until": (end + timedelta(days=1)).isoformat(),
            "search_product": "Latest",
            "default_window_minutes": int(window),
            "limit_per_job": int(limit),
            "minimum_window_minutes": 15,
            "queries": records,
        }
        destination = PROJECT_ROOT / "config" / "generated" / f"{campaign_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        st.success(f"Campaña guardada en {destination.relative_to(PROJECT_ROOT)}")


st.title("X Research Console")
st.markdown(
    '<p class="small-note">Descargas por ventanas exactas, reanudables y auditables. '
    "Las cookies permanecen en esta computadora.</p>",
    unsafe_allow_html=True,
)

download_tab, progress_tab, threads_tab, results_tab, builder_tab = st.tabs(
    ["Descarga", "Progreso", "Hilos", "Resultados", "Nueva campaña"]
)

available = campaign_files()
if not available:
    st.error("No hay campañas válidas en la carpeta config.")
    st.stop()

labels = {str(path.relative_to(PROJECT_ROOT)): path for path in available}
selected_label = st.sidebar.selectbox("Campaña", options=list(labels))
selected = labels[selected_label]
campaign = load_campaign_config(selected)
experiment = generate_experiment(campaign)
metrics = plan_metrics(experiment)
run_paths = paths_for(campaign.campaign_id)
status = process_status(campaign.campaign_id)
thread_run_id = f"{campaign.campaign_id}_hilos"
thread_status = process_status(thread_run_id)

st.sidebar.caption(campaign.description or "Sin descripción")
st.sidebar.write(f"**Período:** {campaign.since} → {campaign.until}")
st.sidebar.write(f"**Trabajos iniciales:** {metrics['jobs']}")
st.sidebar.write("**Estado:** " + ("Ejecutándose" if status["running"] else "Detenido"))

with download_tab:
    st.subheader("Preparar y ejecutar")
    st.info(
        "Cada trabajo usa límites temporales en segundos y descarta cualquier resultado "
        "fuera del período. Si alcanza el máximo, puede subdividirse automáticamente."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Trabajos", metrics["jobs"])
    c2.metric("Consultas", len(campaign.queries))
    c3.metric("Límite por trabajo", campaign.limit_per_job)

    st.markdown("#### Cuentas disponibles")
    render_accounts()

    auto_refine = st.checkbox("Subdividir automáticamente si se alcanza el límite", value=True)
    col_start, col_stop = st.columns([1, 1])
    with col_start:
        if st.button("Iniciar o reanudar", type="primary", disabled=status["running"]):
            arguments = [
                "collect-campaign",
                "--campaign",
                str(selected),
                "--accounts-db",
                str(PROJECT_ROOT / "data" / "accounts.db"),
                "--database",
                str(run_paths["database"]),
                "--raw-dir",
                str(run_paths["raw"]),
                "--plan-output",
                str(run_paths["plan"]),
            ]
            if auto_refine:
                arguments.extend(["--auto-refine", "--max-refinement-rounds", "6"])
            try:
                start_process(campaign.campaign_id, arguments)
            except RuntimeError as error:
                st.error(str(error))
            else:
                st.success("Descarga iniciada. Podés cerrar esta pestaña y volver luego.")
                st.rerun()
    with col_stop:
        if st.button(
            "Detener de forma segura", disabled=not status["running"]
        ) and stop_process(campaign.campaign_id):
            st.warning("Se solicitó la detención. Los tuits ya registrados se conservan.")

    st.caption(f"Datos locales: {run_paths['root'].relative_to(PROJECT_ROOT)}")

with progress_tab:
    st.subheader("Estado de los trabajos")
    rows = job_rows(run_paths["database"])
    counts = database_counts(run_paths["database"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tuits únicos", counts["tweets"])
    m2.metric("Autores", counts["authors"])
    m3.metric("Conversaciones", counts["conversations"])
    m4.metric("Trabajos registrados", counts["jobs"])
    if rows:
        frame = pd.DataFrame(rows)
        st.dataframe(frame, hide_index=True, width="stretch")
    else:
        st.info("La campaña todavía no registró trabajos.")
    if st.button("Actualizar estado"):
        st.rerun()

    with st.expander("Últimas líneas del registro", expanded=bool(status["running"])):
        log = read_log(campaign.campaign_id)
        st.code(log or "Todavía no hay mensajes.", language="text")

with threads_tab:
    st.subheader("Reconstruir conversaciones")
    st.write(
        "Esta etapa se ejecuta después de la búsqueda. Selecciona conversaciones a partir "
        "de los resultados directos y registra cada tuit inmediatamente."
    )
    left, right = st.columns(2)
    with left:
        thread_top = st.number_input(
            "Cantidad máxima de conversaciones",
            min_value=1,
            max_value=10000,
            value=200,
            step=25,
        )
    with right:
        minimum_replies = st.number_input(
            "Mínimo de respuestas declarado",
            min_value=0,
            max_value=1000000,
            value=1,
            step=1,
        )
    h1, h2 = st.columns(2)
    with h1:
        disabled = (
            status["running"]
            or thread_status["running"]
            or not run_paths["database"].exists()
        )
        if st.button("Iniciar o reanudar hilos", type="primary", disabled=disabled):
            arguments = [
                "expand-threads",
                "--database",
                str(run_paths["database"]),
                "--accounts-db",
                str(PROJECT_ROOT / "data" / "accounts.db"),
                "--raw-dir",
                str(run_paths["root"] / "raw_threads"),
                "--plan-output",
                str(run_paths["root"] / "thread_plan.json"),
                "--top",
                str(int(thread_top)),
                "--minimum-replies",
                str(int(minimum_replies)),
                "--since",
                campaign.since,
                "--until",
                campaign.until,
                "--timezone",
                campaign.timezone,
                "--experiment-id",
                thread_run_id,
                "--auto-refine",
                "--max-refinement-rounds",
                "6",
            ]
            try:
                start_process(thread_run_id, arguments)
            except RuntimeError as error:
                st.error(str(error))
            else:
                st.success("Reconstrucción iniciada.")
                st.rerun()
    with h2:
        if st.button(
            "Detener hilos", disabled=not thread_status["running"]
        ) and stop_process(thread_run_id):
            st.warning("Se solicitó la detención; lo registrado permanece guardado.")

    if status["running"]:
        st.info("Esperá a que termine la descarga principal antes de reconstruir hilos.")
    with st.expander("Registro de hilos", expanded=bool(thread_status["running"])):
        st.code(read_log(thread_run_id) or "Todavía no hay mensajes.", language="text")

with results_tab:
    st.subheader("Revisar y exportar")
    counts = database_counts(run_paths["database"])
    if not run_paths["database"].exists():
        st.info("Todavía no hay una base para exportar.")
    else:
        st.write(
            f"La base contiene **{counts['tweets']:,} tuits únicos** y "
            f"**{counts['conversations']:,} conversaciones**."
        )
        export_tweets, export_threads = st.columns(2)
        with export_tweets:
            if st.button("Crear CSV de tuits"):
                amount = ResearchStore(run_paths["database"]).export_tweets_csv(
                    run_paths["tweets_csv"]
                )
                st.success(f"Exportados {amount:,} tuits.")
            if run_paths["tweets_csv"].exists():
                st.download_button(
                    "Descargar tweets.csv",
                    run_paths["tweets_csv"].read_bytes(),
                    file_name=f"{campaign.campaign_id}_tweets.csv",
                )
        with export_threads:
            if st.button("Crear CSV ordenado por conversación"):
                amount = ResearchStore(run_paths["database"]).export_threads_csv(
                    run_paths["threads_csv"]
                )
                st.success(f"Exportadas {amount:,} filas.")
            if run_paths["threads_csv"].exists():
                st.download_button(
                    "Descargar threads.csv",
                    run_paths["threads_csv"].read_bytes(),
                    file_name=f"{campaign.campaign_id}_threads.csv",
                )

with builder_tab:
    render_builder()
