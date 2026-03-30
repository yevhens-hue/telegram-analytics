import pytest
from unittest.mock import patch, MagicMock
from market_data import fetch_ton_price, get_latest_ton_price
from db_utils import init_all_tables

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    import db_utils
    db_path = str(tmp_path / "test_market.db")
    monkeypatch.setattr(db_utils, "DB_FILE", db_path)
    init_all_tables()

def test_fetch_ton_price_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"the-open-network": {"usd": 5.42}}
    mock_resp.status_code = 200
    
    with patch("requests.get", return_value=mock_resp):
        price = fetch_ton_price()
        assert price == 5.42
        
    # Check if saved to DB
    assert get_latest_ton_price() == 5.42

def test_fetch_ton_price_failure():
    with patch("requests.get", side_effect=Exception("API Down")):
        price = fetch_ton_price()
        assert price is None

def test_get_latest_ton_price_empty():
    assert get_latest_ton_price() is None
