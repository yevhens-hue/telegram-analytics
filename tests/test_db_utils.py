"""Tests for db_utils.py — database operations."""
import sqlite3
import pytest
from datetime import datetime

import db_utils


class TestInitAllTables:
    def test_creates_all_tables(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(db_utils, "DB_FILE", db_path)
        monkeypatch.setattr(db_utils, "POSTGRES_URL", None)

        db_utils.init_all_tables()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in c.fetchall()}
        conn.close()

        expected = {"position_history", "ad_campaigns", "channel_stats", "ton_metrics", "app_analytics"}
        assert expected.issubset(tables)

    def test_idempotent(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(db_utils, "DB_FILE", db_path)
        monkeypatch.setattr(db_utils, "POSTGRES_URL", None)

        db_utils.init_all_tables()
        db_utils.init_all_tables()  # Should not raise

    def test_app_analytics_has_unique_constraint(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(db_utils, "DB_FILE", db_path)
        monkeypatch.setattr(db_utils, "POSTGRES_URL", None)

        db_utils.init_all_tables()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='app_analytics'")
        schema = c.fetchone()[0]
        conn.close()

        assert "UNIQUE" in schema.upper()


class TestGetPlaceholder:
    def test_sqlite_placeholder(self, monkeypatch):
        monkeypatch.setattr(db_utils, "POSTGRES_URL", None)
        assert db_utils.get_placeholder() == "?"

    def test_postgres_placeholder(self, monkeypatch):
        monkeypatch.setattr(db_utils, "POSTGRES_URL", "postgresql://fake")
        assert db_utils.get_placeholder() == "%s"


class TestSavePositionHistory:
    def test_saves_single_app(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        apps = [{"name": "TestApp", "description": "A test", "category": "Games", "position": 1}]
        db_utils.save_position_history(apps, date=today)

        c = db_conn.cursor()
        c.execute("SELECT * FROM position_history WHERE app_name = ?", ("TestApp",))
        row = c.fetchone()
        assert row is not None
        assert row["position"] == 1
        assert row["date"] == today

    def test_saves_multiple_apps(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        apps = [
            {"name": "App1", "position": 1},
            {"name": "App2", "position": 2},
            {"name": "App3", "position": 3},
        ]
        db_utils.save_position_history(apps, date=today)

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM position_history")
        assert c.fetchone()[0] == 3

    def test_defaults_to_today(self, db_conn):
        apps = [{"name": "TodayApp", "position": 5}]
        db_utils.save_position_history(apps)

        today = datetime.now().strftime("%Y-%m-%d")
        c = db_conn.cursor()
        c.execute("SELECT date FROM position_history WHERE app_name = ?", ("TodayApp",))
        assert c.fetchone()[0] == today


class TestSaveAdCampaigns:
    def test_saves_campaign(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        records = [{"app_name": "TestApp", "platform": "Adsgram", "estimated_budget": 10000.0, "status": "ACTIVE"}]
        db_utils.save_ad_campaigns(records, date=today)

        c = db_conn.cursor()
        c.execute("SELECT * FROM ad_campaigns WHERE app_name = ?", ("TestApp",))
        row = c.fetchone()
        assert row["platform"] == "Adsgram"
        assert row["estimated_budget"] == 10000.0


class TestSaveChannelStats:
    def test_saves_stats(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        db_utils.save_channel_stats("TestApp", "test_handle", 100000, 5000, 5.0, date=today)

        c = db_conn.cursor()
        c.execute("SELECT * FROM channel_stats WHERE app_name = ?", ("TestApp",))
        row = c.fetchone()
        assert row["subscribers"] == 100000
        assert row["avg_views"] == 5000
        assert row["err"] == 5.0


class TestSaveTonMetrics:
    def test_saves_metrics(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        db_utils.save_ton_metrics("TestApp", "EQAbc123", 1500.5, 2000, date=today)

        c = db_conn.cursor()
        c.execute("SELECT * FROM ton_metrics WHERE app_id = ?", ("TestApp",))
        row = c.fetchone()
        assert row["daily_revenue_ton"] == 1500.5
        assert row["daily_active_wallets"] == 2000


class TestSaveAppAnalytics:
    def test_inserts_record(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        record = {
            "app_name": "TestApp",
            "date": today,
            "position": 1,
            "growth": 5,
            "revenue_ton": 3000.0,
            "dau": 50000,
            "organic_index": 85.0,
            "trend_score": 120.0,
            "market_sentiment": 75.0,
            "prediction_7d": 2,
        }
        db_utils.save_app_analytics(record)

        c = db_conn.cursor()
        c.execute("SELECT * FROM app_analytics WHERE app_name = ?", ("TestApp",))
        row = c.fetchone()
        assert row["position"] == 1
        assert row["growth"] == 5
        assert row["organic_index"] == 85.0

    def test_upserts_on_conflict(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        record1 = {
            "app_name": "TestApp",
            "date": today,
            "position": 5,
            "growth": 0,
            "revenue_ton": 1000.0,
            "dau": 10000,
            "organic_index": 50.0,
            "trend_score": 30.0,
            "market_sentiment": 50.0,
            "prediction_7d": 5,
        }
        record2 = {
            "app_name": "TestApp",
            "date": today,
            "position": 1,
            "growth": 4,
            "revenue_ton": 5000.0,
            "dau": 100000,
            "organic_index": 90.0,
            "trend_score": 150.0,
            "market_sentiment": 80.0,
            "prediction_7d": 1,
        }

        db_utils.save_app_analytics(record1)
        db_utils.save_app_analytics(record2)

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM app_analytics WHERE app_name = ?", ("TestApp",))
        assert c.fetchone()[0] == 1

        c.execute("SELECT * FROM app_analytics WHERE app_name = ?", ("TestApp",))
        row = c.fetchone()
        assert row["position"] == 1
        assert row["revenue_ton"] == 5000.0
        assert row["organic_index"] == 90.0

    def test_default_values(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        record = {
            "app_name": "MinimalApp",
            "date": today,
            "position": 10,
            "growth": -2,
            "revenue_ton": 100.0,
            "dau": 500,
            "organic_index": 20.0,
            "trend_score": 10.0,
        }
        db_utils.save_app_analytics(record)

        c = db_conn.cursor()
        c.execute("SELECT * FROM app_analytics WHERE app_name = ?", ("MinimalApp",))
        row = c.fetchone()
        assert row["ad_spend_est"] == 0
        assert row["is_mock"] == 0
        assert row["market_sentiment"] == 50
