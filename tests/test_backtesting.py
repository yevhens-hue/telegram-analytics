"""Tests for backtesting.py — prediction accuracy analysis."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection
import backtesting


class TestRunBacktest:
    def test_returns_none_when_no_data(self, db_conn):
        result = backtesting.run_backtest()
        assert result is None

    def test_returns_none_when_no_future_data(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=3)).strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute(
            "INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
            ("AppA", past, 10, 5),
        )
        db_conn.commit()

        result = backtesting.run_backtest(days_back=30, prediction_horizon=7)
        assert result is None

    def test_correct_direction_detection(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        now = today.strftime("%Y-%m-%d")

        c = db_conn.cursor()
        # Predicted position 5 from position 10 = predicting improvement
        c.execute(
            "INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
            ("AppA", past, 10, 5),
        )
        # Actual position 6 = also improved (direction correct)
        c.execute(
            "INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
            ("AppA", now, 6, 3),
        )
        db_conn.commit()

        result = backtesting.run_backtest(days_back=30, prediction_horizon=7)
        assert result is not None
        assert result["total_predictions"] == 1
        assert result["direction_accuracy_pct"] == 100.0
        assert result["avg_position_error"] == 1.0  # |5 - 6| = 1

    def test_wrong_direction_detection(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        now = today.strftime("%Y-%m-%d")

        c = db_conn.cursor()
        # Predicted improvement (5 from 10)
        c.execute(
            "INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
            ("AppA", past, 10, 5),
        )
        # Actual worsening (15 from 10) — wrong direction
        c.execute(
            "INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
            ("AppA", now, 15, 12),
        )
        db_conn.commit()

        result = backtesting.run_backtest(days_back=30, prediction_horizon=7)
        assert result is not None
        assert result["direction_accuracy_pct"] == 0.0

    def test_skips_null_predictions(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        now = today.strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute(
            "INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
            ("AppA", past, 10, None),
        )
        c.execute(
            "INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
            ("AppA", now, 5, 3),
        )
        db_conn.commit()

        result = backtesting.run_backtest(days_back=30, prediction_horizon=7)
        assert result is None

    def test_per_app_breakdown(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        now = today.strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", past, 10, 5))
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", now, 6, 4))
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppB", past, 20, 15))
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppB", now, 25, 20))
        db_conn.commit()

        result = backtesting.run_backtest(days_back=30, prediction_horizon=7)
        assert result is not None
        assert "AppA" in result["per_app"]
        assert "AppB" in result["per_app"]
        assert result["per_app"]["AppA"]["predictions"] == 1
        assert result["per_app"]["AppB"]["predictions"] == 1

    def test_saves_result_to_db(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        now = today.strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", past, 10, 5))
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", now, 6, 4))
        db_conn.commit()

        backtesting.run_backtest(days_back=30, prediction_horizon=7)

        c.execute("SELECT COUNT(*) FROM backtest_results")
        assert c.fetchone()[0] >= 1

    def test_report_contains_required_fields(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        now = today.strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", past, 10, 5))
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", now, 6, 4))
        db_conn.commit()

        result = backtesting.run_backtest()
        assert "period_days" in result
        assert "prediction_horizon" in result
        assert "total_predictions" in result
        assert "direction_accuracy_pct" in result
        assert "avg_position_error" in result
        assert "max_position_error" in result
        assert "min_position_error" in result
        assert "per_app" in result


class TestBacktestSummary:
    def test_returns_string(self, db_conn):
        result = backtesting.get_backtest_summary()
        assert isinstance(result, str)

    def test_returns_no_data_message_when_empty(self, db_conn):
        result = backtesting.get_backtest_summary()
        assert "Недостаточно данных" in result

    def test_summary_contains_metrics(self, db_conn):
        today = datetime.now()
        past = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        now = today.strftime("%Y-%m-%d")

        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", past, 10, 5))
        c.execute("INSERT INTO app_analytics (app_name, date, position, prediction_7d) VALUES (?, ?, ?, ?)",
                  ("AppA", now, 6, 4))
        db_conn.commit()

        result = backtesting.get_backtest_summary()
        assert "Backtest Report" in result
        assert "AppA" in result
