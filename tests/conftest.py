import os
import sqlite3
import pytest

# Force SQLite mode for all tests
os.environ.pop("POSTGRES_URL", None)
os.environ["ANALYTICS_DB"] = ":memory:"

# Must import after env setup
import db_utils


@pytest.fixture(autouse=True)
def _patch_db_file(tmp_path, monkeypatch):
    """Redirect DB_FILE to a temp file for each test."""
    db_path = str(tmp_path / "test_analytics.db")
    monkeypatch.setattr(db_utils, "DB_FILE", db_path)
    monkeypatch.setattr(db_utils, "POSTGRES_URL", None)
    # Reset the connection cache used by get_connection
    yield


@pytest.fixture
def db_conn(tmp_path, monkeypatch):
    """Provide a raw SQLite connection with tables initialized."""
    db_path = str(tmp_path / "test_analytics.db")
    monkeypatch.setattr(db_utils, "DB_FILE", db_path)
    monkeypatch.setattr(db_utils, "POSTGRES_URL", None)

    db_utils.init_all_tables()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def seed_today(db_conn):
    """Seed position_history data for today."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    c = db_conn.cursor()
    apps = [
        ("AppOne", "Desc 1", "Games", 1, today),
        ("AppTwo", "Desc 2", "DeFi", 2, today),
        ("AppThree", "Desc 3", "Social", 3, today),
    ]
    c.executemany(
        "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
        apps,
    )
    db_conn.commit()
    return today


@pytest.fixture
def seed_yesterday(db_conn):
    """Seed position_history data for yesterday."""
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    c = db_conn.cursor()
    apps = [
        ("AppOne", "Desc 1", "Games", 3, yesterday),
        ("AppTwo", "Desc 2", "DeFi", 1, yesterday),
        ("AppThree", "Desc 3", "Social", 3, yesterday),
    ]
    c.executemany(
        "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
        apps,
    )
    db_conn.commit()
    return yesterday
