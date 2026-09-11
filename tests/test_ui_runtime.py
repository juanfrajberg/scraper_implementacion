import sqlite3
from unittest.mock import patch

from ui.runtime import (
    account_rows,
    database_counts,
    has_active_account,
    process_status,
    safe_name,
    stop_process,
)


def test_safe_name_removes_unsafe_characters():
    assert safe_name("Ventana 4 / Suiza") == "Ventana_4_Suiza"
    assert safe_name("***") == "campania"


def test_missing_process_is_not_running(tmp_path):
    status = process_status("prueba", tmp_path)
    assert status["running"] is False
    assert status["pid"] is None


def test_completed_child_is_reaped_and_pid_file_removed(tmp_path):
    pid_file = tmp_path / "data" / "runtime" / "prueba.pid.json"
    pid_file.parent.mkdir(parents=True)
    pid_file.write_text('{"pid": 123}', encoding="utf-8")
    with patch("ui.runtime.os.waitpid", return_value=(123, 0)):
        status = process_status("prueba", tmp_path)
    assert status["running"] is False
    assert not pid_file.exists()


def test_stop_process_removes_pid_file(tmp_path):
    pid_file = tmp_path / "data" / "runtime" / "prueba.pid.json"
    pid_file.parent.mkdir(parents=True)
    pid_file.write_text('{"pid": 123}', encoding="utf-8")
    with patch("ui.runtime.process_is_running", return_value=True), patch("ui.runtime.os.killpg"):
        assert stop_process("prueba", tmp_path) is True
    assert not pid_file.exists()


def test_stop_process_handles_stale_or_inaccessible_pid(tmp_path):
    pid_file = tmp_path / "data" / "runtime" / "prueba.pid.json"
    pid_file.parent.mkdir(parents=True)
    pid_file.write_text('{"pid": 123}', encoding="utf-8")
    with (
        patch("ui.runtime.process_is_running", return_value=True),
        patch("ui.runtime.os.killpg", side_effect=PermissionError),
    ):
        assert stop_process("prueba", tmp_path) is False
    assert not pid_file.exists()


def test_account_rows_do_not_expose_cookies(tmp_path):
    database = tmp_path / "accounts.db"
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE accounts (username TEXT, active INTEGER, last_used TEXT, "
            "error_msg TEXT, cookies TEXT)"
        )
        connection.execute("INSERT INTO accounts VALUES ('cuenta', 1, NULL, NULL, 'secreto')")
    rows = account_rows(database)
    assert rows == [{"username": "cuenta", "active": 1, "last_used": None, "error_msg": None}]
    assert has_active_account(rows)
    assert not has_active_account([])
    assert not has_active_account([{"username": "inactiva", "active": 0}])


def test_database_counts(tmp_path):
    database = tmp_path / "research.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE tweets (tweet_id TEXT, author_id TEXT, conversation_id TEXT);
            CREATE TABLE users (user_id TEXT);
            CREATE TABLE jobs (job_id TEXT);
            INSERT INTO tweets VALUES ('1', 'u1', 'c1'), ('2', 'u2', 'c1');
            INSERT INTO users VALUES ('u1'), ('u2');
            INSERT INTO jobs VALUES ('j1');
            """
        )
    assert database_counts(database) == {
        "tweets": 2,
        "authors": 2,
        "conversations": 1,
        "jobs": 1,
    }
