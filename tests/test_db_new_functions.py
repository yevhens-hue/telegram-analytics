"""Tests for db_utils.py — new helper functions (social, price, competitors, backtest)."""
import pytest
from datetime import datetime
from db_utils import (
    init_all_tables, get_connection,
    save_social_mention, save_price_snapshot,
    save_backtest_result, get_competitors, add_competitor_pair,
)


class TestSaveSocialMention:
    def test_inserts_mention(self, db_conn):
        save_social_mention("AppA", "telegram", "Great app!", 75.0, "2025-01-01")

        c = db_conn.cursor()
        c.execute("SELECT app_name, platform, content, sentiment_score FROM social_mentions")
        row = c.fetchone()
        assert row[0] == "AppA"
        assert row[1] == "telegram"
        assert row[2] == "Great app!"
        assert row[3] == 75.0

    def test_defaults_to_today(self, db_conn):
        save_social_mention("AppA", "telegram", "Hello", 50.0)

        c = db_conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT date FROM social_mentions WHERE app_name = 'AppA'")
        assert c.fetchone()[0] == today

    def test_multiple_mentions_same_app(self, db_conn):
        save_social_mention("AppA", "telegram", "Msg 1", 60.0)
        save_social_mention("AppA", "twitter", "Msg 2", 40.0)

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM social_mentions WHERE app_name = 'AppA'")
        assert c.fetchone()[0] == 2


class TestSavePriceSnapshot:
    def test_inserts_price(self, db_conn):
        save_price_snapshot("TON", 5.50, "hourly")

        c = db_conn.cursor()
        c.execute("SELECT asset_id, price_usd, granularity FROM price_history")
        row = c.fetchone()
        assert row[0] == "TON"
        assert row[1] == 5.50
        assert row[2] == "hourly"

    def test_defaults_to_daily(self, db_conn):
        save_price_snapshot("TON", 3.0)

        c = db_conn.cursor()
        c.execute("SELECT granularity FROM price_history WHERE asset_id = 'TON'")
        assert c.fetchone()[0] == "daily"

    def test_multiple_snapshots(self, db_conn):
        save_price_snapshot("TON", 5.0)
        save_price_snapshot("TON", 5.5)
        save_price_snapshot("BTC", 60000.0)

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM price_history")
        assert c.fetchone()[0] == 3


class TestSaveBacktestResult:
    def test_inserts_result(self, db_conn):
        save_backtest_result(30, 10, 75.5, 2.3, '{"test": true}')

        c = db_conn.cursor()
        c.execute("SELECT period_days, total_predictions, direction_accuracy_pct, avg_position_error FROM backtest_results")
        row = c.fetchone()
        assert row[0] == 30
        assert row[1] == 10
        assert row[2] == 75.5
        assert row[3] == 2.3

    def test_stores_json_report(self, db_conn):
        save_backtest_result(7, 5, 80.0, 1.5, '{"apps": ["A", "B"]}')

        c = db_conn.cursor()
        c.execute("SELECT report_json FROM backtest_results")
        assert '"apps"' in c.fetchone()[0]


class TestCompetitorPairs:
    def test_add_and_get_competitors(self, db_conn):
        add_competitor_pair("AppA", "AppB")
        comps = get_competitors("AppA")
        assert "AppB" in comps

    def test_get_returns_both_directions(self, db_conn):
        add_competitor_pair("AppA", "AppB")
        comps = get_competitors("AppB")
        assert "AppA" in comps

    def test_no_duplicates(self, db_conn):
        add_competitor_pair("AppA", "AppB")
        add_competitor_pair("AppA", "AppB")
        comps = get_competitors("AppA")
        assert comps.count("AppB") == 1

    def test_empty_when_no_competitors(self, db_conn):
        comps = get_competitors("NonExistent")
        assert comps == []

    def test_multiple_competitors(self, db_conn):
        add_competitor_pair("AppA", "AppB")
        add_competitor_pair("AppA", "AppC")
        comps = get_competitors("AppA")
        assert len(comps) == 2
        assert "AppB" in comps
        assert "AppC" in comps
