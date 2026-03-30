"""Tests for get_app_detail and get_all_app_names — new db_utils functions."""
import random
import pytest
from datetime import datetime, timedelta

import db_utils


class TestGetAppDetail:
    def _seed_app(self, db_conn, app_name="TestApp", days=3):
        today = datetime.now()
        c = db_conn.cursor()
        for i in range(days):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute(
                "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                (app_name, "Test desc", "Games", i + 1, date_str),
            )
            c.execute(
                "INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES (?, ?, ?, ?, ?)",
                (app_name, "EQTestContract12345678901234567890123456789012", 1000.0 + i * 100, 50000 + i * 1000, date_str),
            )
            c.execute(
                "INSERT INTO channel_stats (app_name, handle, subscribers, avg_views, err, date) VALUES (?, ?, ?, ?, ?, ?)",
                (app_name, "testchannel", 100000, 5000, 5.0, date_str),
            )
            c.execute(
                "INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, organic_index, trend_score, ad_spend_est, is_mock, market_sentiment, prediction_7d) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (app_name, date_str, i + 1, 2 - i, 1000.0 + i * 100, 50000 + i * 1000, 80.0 - i * 5, 60.0 - i * 3, 0, 0, 70.0, max(1, i)),
            )
        db_conn.commit()

    def test_returns_analytics(self, db_conn):
        self._seed_app(db_conn)
        detail = db_utils.get_app_detail("TestApp")
        assert detail["analytics"] is not None

    def test_returns_position_history(self, db_conn):
        self._seed_app(db_conn)
        detail = db_utils.get_app_detail("TestApp")
        assert len(detail["position_history"]) == 3

    def test_returns_analytics_history(self, db_conn):
        self._seed_app(db_conn)
        detail = db_utils.get_app_detail("TestApp")
        assert len(detail["analytics_history"]) == 3

    def test_returns_ton_metrics(self, db_conn):
        self._seed_app(db_conn)
        detail = db_utils.get_app_detail("TestApp")
        assert detail["ton"] is not None

    def test_returns_channel_stats(self, db_conn):
        self._seed_app(db_conn)
        detail = db_utils.get_app_detail("TestApp")
        assert detail["channel"] is not None

    def test_returns_none_for_nonexistent_app(self, db_conn):
        detail = db_utils.get_app_detail("NonExistentApp")
        assert detail["analytics"] is None
        assert detail["ton"] is None
        assert detail["channel"] is None

    def test_returns_empty_lists_for_nonexistent_app(self, db_conn):
        detail = db_utils.get_app_detail("NonExistentApp")
        assert detail["position_history"] == []
        assert detail["analytics_history"] == []

    def test_position_history_limited_to_30(self, db_conn):
        today = datetime.now()
        c = db_conn.cursor()
        for i in range(40):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute(
                "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                ("ManyDays", "Desc", "Games", i + 1, date_str),
            )
        db_conn.commit()

        detail = db_utils.get_app_detail("ManyDays")
        assert len(detail["position_history"]) == 30

    def test_ton_address_returned(self, db_conn):
        self._seed_app(db_conn)
        detail = db_utils.get_app_detail("TestApp")
        assert detail["ton"]["contract_address"].startswith("EQ")

    def test_channel_handle_returned(self, db_conn):
        self._seed_app(db_conn)
        detail = db_utils.get_app_detail("TestApp")
        assert detail["channel"]["handle"] == "testchannel"


class TestGetAllAppNames:
    def test_returns_all_app_names(self, db_conn):
        c = db_conn.cursor()
        apps = [("App1", "d1", "Games", 1), ("App2", "d2", "DeFi", 2), ("App3", "d3", "Social", 3)]
        today = datetime.now().strftime("%Y-%m-%d")
        for name, desc, cat, pos in apps:
            c.execute(
                "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                (name, desc, cat, pos, today),
            )
        db_conn.commit()

        names = db_utils.get_all_app_names()
        assert "App1" in names
        assert "App2" in names
        assert "App3" in names

    def test_returns_sorted_names(self, db_conn):
        c = db_conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        for name in ["Zebra", "Alpha", "Middle"]:
            c.execute(
                "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                (name, "d", "Games", 1, today),
            )
        db_conn.commit()

        names = db_utils.get_all_app_names()
        assert names == sorted(names)

    def test_returns_empty_for_empty_db(self, db_conn):
        names = db_utils.get_all_app_names()
        assert names == []

    def test_no_duplicates(self, db_conn):
        c = db_conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        for date in [today, yesterday]:
            c.execute(
                "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                ("SameApp", "d", "Games", 1, date),
            )
        db_conn.commit()

        names = db_utils.get_all_app_names()
        assert names.count("SameApp") == 1
