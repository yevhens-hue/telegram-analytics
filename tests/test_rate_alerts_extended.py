"""Tests for rate_alerts.py — significant changes and rate-of-change alerts."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection
import rate_alerts


class TestGetSignificantChanges:
    def test_detects_large_position_jump(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 50, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 5, today))
        db_conn.commit()

        changes = rate_alerts.get_significant_changes(threshold=10)
        names = [c["app_name"] for c in changes]
        assert "AppA" in names

    def test_ignores_small_changes(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppB", 10, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppB", 9, today))
        db_conn.commit()

        changes = rate_alerts.get_significant_changes(threshold=10)
        names = [c["app_name"] for c in changes]
        assert "AppB" not in names

    def test_jump_value_is_correct(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 50, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppA", 5, today))
        db_conn.commit()

        changes = rate_alerts.get_significant_changes(threshold=10)
        app_a = next(c for c in changes if c["app_name"] == "AppA")
        assert app_a["jump"] == 45
        assert app_a["prev_pos"] == 50
        assert app_a["curr_pos"] == 5

    def test_returns_empty_when_no_data(self, db_conn):
        changes = rate_alerts.get_significant_changes()
        assert changes == []

    def test_custom_threshold(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppC", 15, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppC", 10, today))
        db_conn.commit()

        changes_strict = rate_alerts.get_significant_changes(threshold=10)
        changes_loose = rate_alerts.get_significant_changes(threshold=3)
        assert "AppC" not in [c["app_name"] for c in changes_strict]
        assert "AppC" in [c["app_name"] for c in changes_loose]

    def test_detects_worsening_positions(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppD", 5, yesterday))
        c.execute("INSERT INTO position_history (app_name, position, date) VALUES (?, ?, ?)", ("AppD", 50, today))
        db_conn.commit()

        changes = rate_alerts.get_significant_changes(threshold=10)
        names = [c["app_name"] for c in changes]
        assert "AppD" in names


class TestDetectRateChanges:
    def test_returns_empty_when_no_data(self, db_conn):
        alerts = rate_alerts.detect_rate_changes()
        assert alerts == []

    def test_detects_revenue_spike(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppA", yesterday, 5, 0, 100.0, 1000, 10.0))
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppA", today, 3, 2, 500.0, 5000, 50.0))
        db_conn.commit()

        alerts = rate_alerts.detect_rate_changes()
        metrics = [a["metric"] for a in alerts]
        assert "revenue_ton" in metrics

    def test_detects_dau_spike(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppB", yesterday, 10, 0, 500.0, 1000, 10.0))
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppB", today, 8, 2, 600.0, 5000, 15.0))
        db_conn.commit()

        alerts = rate_alerts.detect_rate_changes()
        metrics = [a["metric"] for a in alerts]
        assert "dau" in metrics

    def test_no_alert_for_stable_metrics(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppC", yesterday, 5, 1, 500.0, 3000, 20.0))
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppC", today, 4, 2, 510.0, 3100, 21.0))
        db_conn.commit()

        alerts = rate_alerts.detect_rate_changes()
        assert alerts == []

    def test_alert_has_required_fields(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppD", yesterday, 5, 0, 100.0, 1000, 10.0))
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppD", today, 3, 2, 500.0, 5000, 50.0))
        db_conn.commit()

        alerts = rate_alerts.detect_rate_changes()
        if alerts:
            a = alerts[0]
            assert "app_name" in a
            assert "metric" in a
            assert "message" in a
            assert "severity" in a
            assert a["severity"] in ("low", "medium", "high")


class TestRunRateAlerts:
    def test_returns_empty_list_when_no_alerts(self, db_conn):
        result = rate_alerts.run_rate_alerts()
        assert result == []

    def test_returns_alerts_when_changes_detected(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppE", yesterday, 5, 0, 100.0, 1000, 10.0))
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppE", today, 3, 2, 500.0, 5000, 50.0))
        db_conn.commit()

        result = rate_alerts.run_rate_alerts()
        assert len(result) > 0

    def test_saves_alerts_to_history(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppF", yesterday, 5, 0, 100.0, 1000, 10.0))
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, trend_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("AppF", today, 3, 2, 500.0, 5000, 50.0))
        db_conn.commit()

        rate_alerts.run_rate_alerts()

        c.execute("SELECT COUNT(*) FROM alert_history WHERE app_name = 'AppF'")
        assert c.fetchone()[0] > 0
