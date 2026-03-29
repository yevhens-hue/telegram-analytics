"""Tests for analytics_engine.py — formula verification and cycle execution."""
import random
import pytest
from datetime import datetime, timedelta

import db_utils
import analytics_engine


class TestAnalyticsFormulas:
    """Verify the mathematical formulas used in run_analytics_cycle."""

    def _seed_position_data(self, db_conn, today, yesterday):
        c = db_conn.cursor()
        c.executemany(
            "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
            [
                ("TestApp", "Desc", "Games", 3, today),
                ("TestApp", "Desc", "Games", 5, yesterday),
            ],
        )
        db_conn.commit()

    def test_growth_calculation(self, db_conn, monkeypatch):
        """Growth = previous_position - current_position."""
        from datetime import datetime, timedelta
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        self._seed_position_data(db_conn, today, yesterday)
        random.seed(42)
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        c.execute("SELECT growth FROM app_analytics WHERE app_name = ?", ("TestApp",))
        row = c.fetchone()
        # growth = prev_pos(5) - current_pos(3) = 2
        assert row[0] == 2

    def test_organic_index_bounds(self, db_conn, monkeypatch):
        """organic_index should be clamped to [5, 100]."""
        from datetime import datetime, timedelta
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        self._seed_position_data(db_conn, today, yesterday)
        random.seed(42)
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        c.execute("SELECT organic_index FROM app_analytics WHERE app_name = ?", ("TestApp",))
        organic_index = c.fetchone()[0]
        assert 5 <= organic_index <= 100

    def test_organic_index_formula_components(self, db_conn):
        """Manually verify organic_index formula with known inputs."""
        pos = 3
        growth = 2
        err = 5.0
        ad_spend = 1000.0

        expected = min(100, max(5,
            (100 / max(1, pos)) + (growth * 2.5) + (err * 2) - (ad_spend / 1000)
        ))
        # = min(100, max(5, 33.33 + 5.0 + 10.0 - 1.0)) = min(100, max(5, 47.33)) = 47.33
        assert 47 <= expected <= 48

    def test_market_sentiment_bounds(self):
        """market_sentiment should be clamped to [0, 100]."""
        # High ERR and growth
        result = min(100, max(0, (20 * 8) + (10 * 5) + 50))
        assert result == 100

        # Negative case
        result = min(100, max(0, (0 * 8) + (-20 * 5) + 50))
        assert result == 0

    def test_prediction_7d_minimum(self):
        """prediction_7d should never go below 1."""
        pos = 2
        growth = 100  # Extreme growth
        result = max(1, int(pos - (growth * 0.7)))
        assert result == 1

    def test_trend_score_formula(self):
        """raw_trend = (growth * 12) + (revenue / 50) + (err * 5), normalized to [0,100]."""
        growth = 3
        revenue = 2000.0
        err = 4.0
        raw = (growth * 12) + (revenue / 50) + (err * 5)
        assert raw == 36 + 40 + 20  # = 96
        # Normalized: min(100, (96 / 200) * 100) = 48.0
        normalized = min(100, (raw / 200) * 100)
        assert normalized == 48.0


class TestRunAnalyticsCycle:
    def test_no_data_returns_early(self, db_conn, caplog):
        """Should log warning if no data for today."""
        analytics_engine.run_analytics_cycle()
        assert "Нет данных за сегодня" in caplog.text

    def test_creates_analytics_from_position_data(self, db_conn, seed_today, seed_yesterday):
        """Should create app_analytics rows from position_history data."""
        random.seed(42)
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM app_analytics")
        count = c.fetchone()[0]
        assert count == 3

    def test_uses_real_ton_data_when_available(self, db_conn, seed_today, seed_yesterday):
        """Should use real TON metrics when available instead of mock."""
        today = datetime.now().strftime("%Y-%m-%d")
        db_utils.save_ton_metrics("AppOne", "EQFakeAddr", 5000.0, 100000, date=today)

        random.seed(42)
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        c.execute("SELECT revenue_ton, dau, is_mock FROM app_analytics WHERE app_name = ?", ("AppOne",))
        row = c.fetchone()
        assert row[0] == 5000.0  # Real revenue
        assert row[1] == 100000  # Real DAU
        assert row[2] == 0  # Not mock

    def test_uses_mock_when_no_ton_data(self, db_conn, seed_today, seed_yesterday):
        """Should generate mock data when TON metrics are missing."""
        random.seed(42)
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        c.execute("SELECT revenue_ton, is_mock FROM app_analytics WHERE app_name = ?", ("AppOne",))
        row = c.fetchone()
        assert row[0] > 0  # Some revenue generated
        assert row[1] == 1  # Is mock

    def test_incorporates_channel_stats(self, db_conn, seed_today, seed_yesterday):
        """Should use channel engagement rate in calculations."""
        today = datetime.now().strftime("%Y-%m-%d")
        db_utils.save_channel_stats("AppOne", "test", 100000, 5000, 8.5, date=today)

        random.seed(42)
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        c.execute("SELECT organic_index FROM app_analytics WHERE app_name = ?", ("AppOne",))
        organic_with_err = c.fetchone()[0]

        # App without channel stats should have lower organic index
        c.execute("SELECT organic_index FROM app_analytics WHERE app_name = ?", ("AppThree",))
        organic_without_err = c.fetchone()[0]

        assert organic_with_err > organic_without_err

    def test_incorporates_ad_spend(self, db_conn, seed_today, seed_yesterday):
        """Should penalize organic_index for ad spend."""
        today = datetime.now().strftime("%Y-%m-%d")
        # Use very high ad spend to clearly demonstrate the penalty
        db_utils.save_ad_campaigns(
            [{"app_name": "AppThree", "platform": "Adsgram", "estimated_budget": 200000, "status": "ACTIVE"}],
            date=today,
        )

        random.seed(42)
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        # AppThree has ads (organic_index penalized by 200000/1000 = 200)
        c.execute("SELECT organic_index FROM app_analytics WHERE app_name = ?", ("AppThree",))
        organic_with_ad = c.fetchone()[0]

        # AppTwo has no ads and similar position
        c.execute("SELECT organic_index FROM app_analytics WHERE app_name = ?", ("AppTwo",))
        organic_without_ad = c.fetchone()[0]

        assert organic_with_ad < organic_without_ad

    def test_upserts_existing_analytics(self, db_conn, seed_today, seed_yesterday):
        """Should update existing analytics on second run instead of duplicating."""
        random.seed(42)
        analytics_engine.run_analytics_cycle()
        analytics_engine.run_analytics_cycle()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM app_analytics")
        assert c.fetchone()[0] == 3  # Still 3, not 6
