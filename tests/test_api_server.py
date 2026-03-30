"""Tests for api_server.py — REST API endpoints."""
import pytest
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection, save_social_mention, save_backtest_result
from unittest.mock import patch, MagicMock

try:
    from fastapi.testclient import TestClient
    from api_server import create_app
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


@pytest.fixture
def api_client(db_conn):
    """Create a test client for the API."""
    if not HAS_FASTAPI:
        pytest.skip("FastAPI not installed")

    # Seed some test data
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    c = db_conn.cursor()
    c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, organic_index, trend_score, market_sentiment, prediction_7d) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              ("AppA", today, 1, 5, 1000.0, 50000, 85.0, 75.0, 80.0, 2))
    c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, organic_index, trend_score, market_sentiment, prediction_7d) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              ("AppB", today, 2, -2, 500.0, 30000, 40.0, 30.0, 50.0, 3))
    c.execute("INSERT INTO alert_history (app_name, message, date, status) VALUES (?, ?, ?, ?)",
              ("AppA", "Test alert", today, "sent"))
    db_conn.commit()

    save_social_mention("AppA", "telegram", "Great news!", 85.0, today)
    save_backtest_result(30, 5, 80.0, 2.0, '{"test": true}')

    app = create_app()
    return TestClient(app)


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestAppsEndpoint:
    def test_returns_list_of_apps(self, api_client):
        resp = api_client.get("/api/apps")
        assert resp.status_code == 200
        data = resp.json()
        assert "apps" in data
        assert len(data["apps"]) == 2

    def test_returns_correct_app_structure(self, api_client):
        resp = api_client.get("/api/apps")
        data = resp.json()
        app = data["apps"][0]
        assert "app_name" in app
        assert "position" in app
        assert "trend_score" in app

    def test_limits_results(self, api_client):
        resp = api_client.get("/api/apps?limit=1")
        data = resp.json()
        assert len(data["apps"]) == 1

    def test_date_filter(self, api_client):
        resp = api_client.get("/api/apps?date=2020-01-01")
        data = resp.json()
        assert len(data["apps"]) == 0


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestAppDetailEndpoint:
    def test_returns_app_history(self, api_client):
        resp = api_client.get("/api/apps/AppA")
        assert resp.status_code == 200
        data = resp.json()
        assert data["app_name"] == "AppA"
        assert "history" in data
        assert len(data["history"]) >= 1

    def test_returns_404_for_unknown_app(self, api_client):
        resp = api_client.get("/api/apps/NonExistent")
        assert resp.status_code == 404


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestSignalsEndpoint:
    def test_returns_signals(self, api_client):
        resp = api_client.get("/api/signals")
        assert resp.status_code == 200
        data = resp.json()
        assert "signals" in data

    def test_filters_by_min_trend(self, api_client):
        resp = api_client.get("/api/signals?min_trend=50")
        data = resp.json()
        for signal in data["signals"]:
            assert signal["trend_score"] >= 50


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestAlertsEndpoint:
    def test_returns_alerts(self, api_client):
        resp = api_client.get("/api/alerts")
        assert resp.status_code == 200
        data = resp.json()
        assert "alerts" in data
        assert len(data["alerts"]) >= 1

    def test_alert_has_message(self, api_client):
        resp = api_client.get("/api/alerts")
        data = resp.json()
        assert "message" in data["alerts"][0]


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestTrendEndpoint:
    def test_returns_trend_data(self, api_client):
        resp = api_client.get("/api/trend")
        assert resp.status_code == 200
        data = resp.json()
        assert "trend" in data


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestSocialEndpoint:
    def test_returns_social_mentions(self, api_client):
        resp = api_client.get("/api/social/AppA")
        assert resp.status_code == 200
        data = resp.json()
        assert "mentions" in data


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestBacktestEndpoint:
    def test_returns_backtest_results(self, api_client):
        resp = api_client.get("/api/backtest")
        assert resp.status_code == 200
        data = resp.json()
        assert "backtests" in data


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestHealthEndpoint:
    def test_returns_ok(self, api_client):
        resp = api_client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
