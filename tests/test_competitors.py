import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from db_utils import init_all_tables, get_connection, add_competitor_pair
import analytics_engine

@pytest.fixture
def setup_competitors(tmp_path, monkeypatch):
    import db_utils
    db_path = str(tmp_path / "test_comp.db")
    monkeypatch.setattr(db_utils, "DB_FILE", db_path)
    init_all_tables()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    with get_connection() as conn:
        c = conn.cursor()
        # Seed AppA and AppB as competitors
        # AppA is doing great (pos 1), AppB is doing okay (pos 10)
        c.execute("INSERT INTO position_history (app_name, position, date, category) VALUES (?, ?, ?, ?)", ("AppA", 1, today, "Games"))
        c.execute("INSERT INTO position_history (app_name, position, date, category) VALUES (?, ?, ?, ?)", ("AppB", 10, today, "Games"))
        
    add_competitor_pair("AppA", "AppB")
    return today

def test_competitor_index_calculation(setup_competitors):
    # This feature doesn't exist yet, we check if analytics_engine calculates relative rank
    with patch("analytics_engine.analyze_channel_sentiment", return_value=50.0):
        analytics_engine.run_analytics_cycle()
        
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT app_name, organic_index FROM app_analytics WHERE app_name IN ('AppA', 'AppB')")
        results = dict(c.fetchall())
        
        # We expect AppA (pos 1) to have a much higher organic_index than AppB (pos 10)
        # especially if we factor in competitor dominance
        assert results["AppA"] > results["AppB"]
        # In the new logic, we'll store competitor dominance somewhere or affect organic_index
