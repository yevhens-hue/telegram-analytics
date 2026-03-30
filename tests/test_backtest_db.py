import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection
import backtesting
import json

@pytest.fixture
def seed_backtest_data(tmp_path, monkeypatch):
    import db_utils
    db_path = str(tmp_path / "test_bt_db.db")
    monkeypatch.setattr(db_utils, "DB_FILE", db_path)
    init_all_tables()
    
    today = datetime.now().strftime("%Y-%m-%d")
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    with get_connection() as conn:
        c = conn.cursor()
        # Seed App with prediction and actual position later
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)", ("AppA", seven_days_ago, 10, 5))
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)", ("AppA", today, 6, 4))
        
    return today

def test_run_backtest_saves_to_db(seed_backtest_data):
    # This should call save_backtest_result
    report = backtesting.run_backtest()
    assert report is not None
    
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT run_date, direction_accuracy_pct FROM backtest_results")
        row = c.fetchone()
        assert row is not None
        assert row[1] == report["direction_accuracy_pct"]
