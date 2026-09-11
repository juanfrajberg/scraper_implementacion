# X Research Console

Aplicación local para recolectar publicaciones públicas de X con **twscrape**, dividir las
búsquedas en períodos pequeños, retomar interrupciones, reconstruir conversaciones y exportar
resultados sin editar archivos de Python.

La interfaz corre en la computadora del investigador. Las cookies, las bases y las descargas no
se publican en GitHub.

## Qué mejora

- usa límites exactos `since_time` y `until_time` en la zona horaria de Argentina;
- descarta resultados que X entregue fuera del período;
- divide cada campaña por día, hora o intervalos menores;
- registra cada tuit inmediatamente en SQLite y JSONL;
- permite detener y reanudar sin duplicar publicaciones;
- marca trabajos saturados y puede subdividirlos automáticamente;
- conserva consulta, capa, período, computadora y tipo de captura;
- separa resultados directos de respuestas incorporadas al reconstruir hilos;
- permite repartir trabajos entre varias computadoras;
- exporta tuits únicos y conversaciones ordenadas a CSV;
- muestra cuentas, progreso, errores y resultados en una interfaz gráfica.

## Empezar

### 1. Preparar Python

En macOS o Linux:

```bash
git clone https://github.com/juanfrajberg/scraper_implementacion.git
cd scraper_implementacion
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,mass]"
```

En Windows, la activación es:

```powershell
.venv\Scripts\activate
```

### 2. Agregar una cuenta de X

```bash
twscrape --db data/accounts.db add_cookie cuenta_investigacion
```

Cuando lo solicite, pegar ambas cookies en una sola línea:

```text
auth_token=VALOR; ct0=VALOR
```

Las cookies permiten acceder a la sesión. No deben compartirse ni subirse al repositorio.

Si una cuenta aparece como **Inactiva** o muestra `Could not authenticate you`, repetí el mismo
comando con cookies nuevas y el mismo nombre. `twscrape` actualizará esa cuenta sin crear un
duplicado.

### 3. Abrir la interfaz

```bash
streamlit run app.py
```

Se abrirá `http://localhost:8501` en el navegador.

### 4. Ejecutar una campaña

1. Elegir una campaña en la barra lateral.
2. Revisar período, consultas, límite y cuentas activas.
3. Presionar **Iniciar o reanudar**.
4. Consultar la pestaña **Progreso**.
5. Cuando termine la búsqueda, abrir **Hilos** para reconstruir conversaciones.
6. Crear y descargar los CSV desde **Resultados**.

Cerrar la pestaña del navegador no detiene la descarga. El botón **Detener de forma segura**
conserva todo lo que ya fue registrado; al reiniciar, los trabajos completos se omiten.

## Campañas preparadas

| Campaña | Período incluido | Consultas |
|---|---|---|
| Ventana 3 — Egipto | 06/07/2026–10/07/2026 | Paraguas, eje Egipto y `fifamedia` |
| Ventana 4 — Suiza | 11/07/2026–14/07/2026 | Paraguas y eje Suiza |
| Ventana 5 — Inglaterra | 15/07/2026–18/07/2026 | Paraguas y eje Inglaterra |

Las fechas visibles son inclusivas. Internamente se convierten a intervalos semiabiertos exactos,
por ejemplo `[2026-07-11 00:00, 2026-07-15 00:00)`, en
`America/Argentina/Buenos_Aires`.

## Archivos locales

Cada campaña se guarda en:

```text
data/runs/<campaña>/
├── research.sqlite3
├── plan.json
├── thread_plan.json
├── raw/
├── raw_threads/
└── exports/
    ├── tweets.csv
    └── threads.csv
```

Todo `data/` está excluido de Git, incluido `accounts.db`.

## Uso por Terminal

La interfaz utiliza el mismo motor que estos comandos:

```bash
x-research validate-campaign \
  --campaign config/ventana_04_cuartos_suiza_2026.json

x-research collect-campaign \
  --campaign config/ventana_04_cuartos_suiza_2026.json \
  --accounts-db data/accounts.db \
  --database data/runs/ventana_04_cuartos_suiza_2026/research.sqlite3 \
  --raw-dir data/runs/ventana_04_cuartos_suiza_2026/raw \
  --auto-refine
```

Para repartir la campaña entre tres computadoras se usa, respectivamente:

```text
--shard-count 3 --shard-index 0
--shard-count 3 --shard-index 1
--shard-count 3 --shard-index 2
```

Las bases resultantes pueden combinarse con `x-research merge-db`.

## Comprobar el proyecto

Estas pruebas no se conectan a X:

```bash
pytest
x-research validate-config
x-research validate-campaign
x-research validate-campaign --campaign config/ventana_03_octavos_egipto_2026.json
x-research validate-campaign --campaign config/ventana_04_cuartos_suiza_2026.json
x-research validate-campaign --campaign config/ventana_05_semifinal_inglaterra_2026.json
```

## Seguridad y alcance

- No subir `accounts.db`, cookies, contraseñas o archivos `.env`.
- No desplegar públicamente la interfaz con credenciales reales.
- Trabajar únicamente con cuentas autorizadas.
- Registrar límites, bloqueos y datos faltantes en el informe de investigación.
- Distinguir los resultados directos del contexto agregado mediante conversaciones.
- Respetar las condiciones de X y los requisitos éticos e institucionales del proyecto.

La interfaz no garantiza exhaustividad: X puede limitar, ordenar o bloquear resultados. El sistema
registra saturación, errores y procedencia para que esas limitaciones sean analizables.
