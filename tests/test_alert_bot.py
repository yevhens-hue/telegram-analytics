"""Tests for alert_bot.py — signal formatting and retrieval."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import db_utils
import alert_bot


class TestFormatAlert:
    """Tests for the pure function format_alert."""

    def test_rocket_emoji_for_high_growth(self):
        signal = ("BigApp", 10, 150.0, 80.0, 1, 75.0)
        result = alert_bot.format_alert(signal)
        assert result.startswith("🚀")
        assert "BigApp" in result

    def test_fire_emoji_for_low_growth(self):
        signal = ("SlowApp", 3, 50.0, 60.0, 5, 60.0)
        result = alert_bot.format_alert(signal)
        assert result.startswith("🔥")
        assert "SlowApp" in result

    def test_contains_all_metrics(self):
        signal = ("TestApp", 8, 120.5, 85.0, 2, 90.0)
        result = alert_bot.format_alert(signal)
        assert "Growth: +8" in result
        assert "120.5" in result  # trend score
        assert "#2" in result  # prediction
        assert "85%" in result  # organic
        assert "90/100" in result  # sentiment

    def test_exact_growth_boundary(self):
        """Growth of exactly 5 should get fire emoji (> 5 means rocket)."""
        signal = ("EdgeApp", 5, 100.0, 50.0, 3, 50.0)
        result = alert_bot.format_alert(signal)
        assert result.startswith("🔥")

    def test_growth_of_6_gets_rocket(self):
        signal = ("EdgeApp", 6, 100.0, 50.0, 3, 50.0)
        result = alert_bot.format_alert(signal)
        assert result.startswith("🚀")


class TestGetAlphaSignals:
    def test_returns_high_trend_signals(self, db_conn, seed_today):
        today = datetime.now().strftime("%Y-%m-%d")
        record = {
            "app_name": "AppOne",
            "date": today,
            "position": 1,
            "growth": 10,
            "revenue_ton": 5000.0,
            "dau": 100000,
            "organic_index": 90.0,
            "trend_score": 150.0,
            "market_sentiment": 80.0,
            "prediction_7d": 1,
        }
        db_utils.save_app_analytics(record)

        signals = alert_bot.get_alpha_signals()
        assert len(signals) >= 1
        names = [s[0] for s in signals]
        assert "AppOne" in names

    def test_filters_low_trend_scores(self, db_conn, seed_today):
        today = datetime.now().strftime("%Y-%m-%d")
        record = {
            "app_name": "LowTrend",
            "date": today,
            "position": 10,
            "growth": 0,
            "revenue_ton": 10.0,
            "dau": 100,
            "organic_index": 10.0,
            "trend_score": 3.0,  # Below threshold of 5
            "market_sentiment": 30.0,
            "prediction_7d": 10,
        }
        db_utils.save_app_analytics(record)

        signals = alert_bot.get_alpha_signals()
        names = [s[0] for s in signals]
        assert "LowTrend" not in names

    def test_limits_to_5(self, db_conn, seed_today):
        today = datetime.now().strftime("%Y-%m-%d")
        for i in range(10):
            record = {
                "app_name": f"App{i}",
                "date": today,
                "position": i + 1,
                "growth": 5,
                "revenue_ton": 1000.0,
                "dau": 10000,
                "organic_index": 50.0,
                "trend_score": 100.0 - i,
                "market_sentiment": 50.0,
                "prediction_7d": i + 1,
            }
            db_utils.save_app_analytics(record)

        signals = alert_bot.get_alpha_signals()
        assert len(signals) == 5

    def test_ordered_by_trend_score_desc(self, db_conn, seed_today):
        today = datetime.now().strftime("%Y-%m-%d")
        for i, score in enumerate([50, 200, 100]):
            record = {
                "app_name": f"OrderApp{i}",
                "date": today,
                "position": i + 1,
                "growth": 5,
                "revenue_ton": 1000.0,
                "dau": 10000,
                "organic_index": 50.0,
                "trend_score": score,
                "market_sentiment": 50.0,
                "prediction_7d": i + 1,
            }
            db_utils.save_app_analytics(record)

        signals = alert_bot.get_alpha_signals()
        scores = [s[2] for s in signals]
        assert scores == sorted(scores, reverse=True)


class TestRunAlerts:
    def test_logs_when_no_signals(self, caplog, db_conn):
        import logging
        with caplog.at_level(logging.INFO, logger="alert_bot"):
            with patch.object(alert_bot, "get_alpha_signals", return_value=[]):
                alert_bot.run_alerts()
        assert "Нет значимых альфа-сигналов" in caplog.text

    def test_sends_to_telegram_when_configured(self, db_conn):
        signals = [("TestApp", 10, 150.0, 80.0, 1, 75.0)]
        with patch.object(alert_bot, "get_alpha_signals", return_value=signals):
            with patch("alert_bot.requests.post") as mock_post:
                with patch.object(alert_bot, "BOT_TOKEN", "fake_token"):
                    with patch.object(alert_bot, "CHAT_ID", "fake_chat"):
                        alert_bot.run_alerts()

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert "fake_token" in call_kwargs[0][0]
        assert call_kwargs[1]["json"]["chat_id"] == "fake_chat"

    def test_does_not_send_without_token(self, db_conn):
        signals = [("TestApp", 10, 150.0, 80.0, 1, 75.0)]
        with patch.object(alert_bot, "get_alpha_signals", return_value=signals):
            with patch("alert_bot.requests.post") as mock_post:
                with patch.object(alert_bot, "BOT_TOKEN", None):
                    with patch.object(alert_bot, "CHAT_ID", None):
                        alert_bot.run_alerts()

        mock_post.assert_not_called()

    def test_saves_alert_to_history(self, db_conn):
        signals = [("HistoryApp", 10, 150.0, 80.0, 1, 75.0)]
        with patch.object(alert_bot, "get_alpha_signals", return_value=signals):
            with patch("alert_bot.requests.post"):
                with patch.object(alert_bot, "BOT_TOKEN", "fake_token"):
                    with patch.object(alert_bot, "CHAT_ID", "fake_chat"):
                        alert_bot.run_alerts()
                        
        c = db_conn.cursor()
        c.execute("SELECT app_name FROM alert_history WHERE app_name = 'HistoryApp'")
        res = c.fetchone()
        assert res is not None
        assert res[0] == "HistoryApp"
