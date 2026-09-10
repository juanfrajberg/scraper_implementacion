import sqlite3

from ui.runtime import account_rows, database_counts, process_status, safe_name


def test_safe_name_removes_unsafe_characters():
    assert safe_name("Ventana 4 / Suiza") == "Ventana_4_Suiza"
    assert safe_name("***") == "campania"


def test_missing_process_is_not_running(tmp_path):
    status = process_status("prueba", tmp_path)
    assert status["running"] is False
    assert status["pid"] is None


def test_account_rows_do_not_expose_cookies(tmp_path):
    database = tmp_path / "accounts.db"
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE accounts (username TEXT, active INTEGER, last_used TEXT, "
            "error_msg TEXT, cookies TEXT)"
        )
        connection.execute(
            "INSERT INTO accounts VALUES ('cuenta', 1, NULL, NULL, 'secreto')"
        )
    rows = account_rows(database)
    assert rows == [
        {"username": "cuenta", "active": 1, "last_used": None, "error_msg": None}
    ]


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
