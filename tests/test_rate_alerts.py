import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection
import rate_alerts

@pytest.fixture
def seed_position_shift(tmp_path, monkeypatch):
    import db_utils
    db_path = str(tmp_path / "test_rate.db")
    monkeypatch.setattr(db_utils, "DB_FILE", db_path)
    init_all_tables()
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    with get_connection() as conn:
        c = conn.cursor()
        # AppA: Big jump (pos 50 -> 5)
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 50, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 5, today))
        
        # AppB: Small move (pos 10 -> 9)
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppB", 10, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppB", 9, today))
        
    return today, yesterday

def test_detect_significant_changes(seed_position_shift):
    changes = rate_alerts.get_significant_changes(threshold=10)
    names = [c["app_name"] for c in changes]
    assert "AppA" in names
    assert "AppB" not in names
    
    # Verify jump value
    app_a_change = next(c for c in changes if c["app_name"] == "AppA")
    assert app_a_change["jump"] == 45 # 50 - 5
