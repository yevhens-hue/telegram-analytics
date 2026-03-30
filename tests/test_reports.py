import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import reports
from db_utils import init_all_tables

@pytest.fixture
def mock_db_data(monkeypatch, tmp_path):
    # Setup test DB
    db_path = str(tmp_path / "test_reports.db")
    import db_utils
    monkeypatch.setattr(db_utils, "DB_FILE", db_path)
    init_all_tables()
    
    # Seed data
    from db_utils import get_connection
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    with get_connection() as conn:
        c = conn.cursor()
        # Seed 2 apps with different growth
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 10, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 5, today)) # growth 5
        
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppB", 20, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppB", 18, today)) # growth 2
        
        c.execute("INSERT INTO app_analytics (app_name, date, trend_score, position, growth) VALUES (?, ?, ?, ?, ?)", ("AppA", today, 80, 5, 5))
        c.execute("INSERT INTO app_analytics (app_name, date, trend_score, position, growth) VALUES (?, ?, ?, ?, ?)", ("AppB", today, 40, 18, 2))

def test_generate_weekly_report_top_growth(mock_db_data):
    """Should return the app with highest growth."""
    report = reports.generate_weekly_report()
    assert "AppA" in report
    assert "5" in report # growth value
    assert "AppB" in report # it should be there but maybe lower
