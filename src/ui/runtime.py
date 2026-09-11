from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProcessFiles:
    pid: Path
    log: Path


def safe_name(value: str) -> str:
    cleaned = "".join(
        character if character.isalnum() or character in "-_" else "_" for character in value
    )
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned.strip("_-") or "campania"


def process_files(run_id: str, root: Path = PROJECT_ROOT) -> ProcessFiles:
    runtime = root / "data" / "runtime"
    name = safe_name(run_id)
    return ProcessFiles(pid=runtime / f"{name}.pid.json", log=runtime / f"{name}.log")


def _read_pid(path: Path) -> int | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return int(value["pid"])
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def process_is_running(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    # A detached worker remains briefly as a zombie until its parent collects
    # the exit status. Reap it without blocking so a completed campaign does
    # not keep appearing as "Ejecutándose" in Streamlit.
    if hasattr(os, "waitpid"):
        try:
            finished_pid, _ = os.waitpid(pid, os.WNOHANG)
            if finished_pid == pid:
                return False
        except ChildProcessError:
            pass
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def process_status(run_id: str, root: Path = PROJECT_ROOT) -> dict[str, Any]:
    files = process_files(run_id, root)
    pid = _read_pid(files.pid)
    running = process_is_running(pid)
    if pid and not running:
        files.pid.unlink(missing_ok=True)
    return {
        "run_id": safe_name(run_id),
        "pid": pid,
        "running": running,
        "log": files.log,
        "pid_file": files.pid,
    }


def start_process(
    run_id: str,
    arguments: Sequence[str],
    *,
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    current = process_status(run_id, root)
    if current["running"]:
        raise RuntimeError(f"El proceso {run_id} ya está ejecutándose")

    files = process_files(run_id, root)
    files.pid.parent.mkdir(parents=True, exist_ok=True)
    files.log.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "x_research.cli", *arguments]
    log_handle = files.log.open("a", encoding="utf-8")
    try:
        process = subprocess.Popen(
            command,
            cwd=root,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )
    finally:
        log_handle.close()

    files.pid.write_text(
        json.dumps({"pid": process.pid, "command": command}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return process_status(run_id, root)


def stop_process(run_id: str, root: Path = PROJECT_ROOT) -> bool:
    status = process_status(run_id, root)
    pid = status["pid"]
    if not status["running"] or not pid:
        status["pid_file"].unlink(missing_ok=True)
        return False
    try:
        if hasattr(os, "killpg"):
            os.killpg(pid, signal.SIGINT)
        else:
            os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        status["pid_file"].unlink(missing_ok=True)
        return False
    except PermissionError:
        # The worker may already have exited while Streamlit was rerunning the
        # page. In that case the stored PID is stale (or has been reused), so
        # it must never be signalled again.
        status["pid_file"].unlink(missing_ok=True)
        return False
    status["pid_file"].unlink(missing_ok=True)
    return True


def read_log(run_id: str, *, lines: int = 120, root: Path = PROJECT_ROOT) -> str:
    path = process_files(run_id, root).log
    try:
        content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return ""
    return "\n".join(content[-max(1, lines) :])


def account_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with sqlite3.connect(path) as database:
            database.row_factory = sqlite3.Row
            rows = database.execute(
                """
                SELECT username, active, last_used, error_msg
                FROM accounts
                ORDER BY username
                """
            ).fetchall()
    except sqlite3.Error:
        return []
    return [dict(row) for row in rows]


def has_active_account(rows: Sequence[dict[str, Any]]) -> bool:
    return any(bool(row.get("active")) for row in rows)


def job_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with sqlite3.connect(path) as database:
            database.row_factory = sqlite3.Row
            rows = database.execute(
                """
                SELECT experiment_id, query_family, corpus_layer, since_date,
                       until_date, status, attempt_count, search_count,
                       unique_count, warning_count, saturated, error_message
                FROM jobs
                ORDER BY since_date, query_family
                """
            ).fetchall()
    except sqlite3.Error:
        return []
    return [dict(row) for row in rows]


def database_counts(path: Path) -> dict[str, int]:
    empty = {"tweets": 0, "authors": 0, "conversations": 0, "jobs": 0}
    if not path.exists():
        return empty
    try:
        with sqlite3.connect(path) as database:
            row = database.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM tweets) AS tweets,
                    (SELECT COUNT(*) FROM users) AS authors,
                    (SELECT COUNT(DISTINCT conversation_id) FROM tweets
                        WHERE conversation_id IS NOT NULL) AS conversations,
                    (SELECT COUNT(*) FROM jobs) AS jobs
                """
            ).fetchone()
    except sqlite3.Error:
        return empty
    return dict(zip(empty, (int(value or 0) for value in row), strict=True))


def run_streamlit() -> None:
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(PROJECT_ROOT / "app.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )
