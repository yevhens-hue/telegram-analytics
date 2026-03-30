"""Tests for seed_mock_data.py — mock data seeding."""
import random
import pytest
from datetime import datetime, timedelta

import db_utils
import seed_mock_data


class TestInitMockData:
    def test_seeds_position_history(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM position_history")
        count = c.fetchone()[0]
        assert count > 0

    def test_seeds_1000_unique_apps(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(DISTINCT app_name) FROM position_history")
        count = c.fetchone()[0]
        assert count >= 900

    def test_seeds_ton_metrics(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM ton_metrics")
        count = c.fetchone()[0]
        assert count > 0

    def test_creates_7_days_of_data(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(DISTINCT date) FROM position_history")
        count = c.fetchone()[0]
        assert count == 7

    def test_skips_if_data_exists(self, db_conn, caplog):
        import logging
        seed_mock_data.init_mock_data()
        with caplog.at_level(logging.INFO, logger="seed_mock_data"):
            seed_mock_data.init_mock_data()

        assert "Данные уже существуют" in caplog.text

    def test_positions_are_positive(self, db_conn):
        random.seed(42)
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT MIN(position) FROM position_history")
        min_pos = c.fetchone()[0]
        assert min_pos >= 1

    def test_revenue_is_positive(self, db_conn):
        random.seed(42)
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT MIN(daily_revenue_ton) FROM ton_metrics")
        min_rev = c.fetchone()[0]
        assert min_rev > 0

    def test_dau_is_positive(self, db_conn):
        random.seed(42)
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT MIN(daily_active_wallets) FROM ton_metrics")
        min_dau = c.fetchone()[0]
        assert min_dau > 0

    def test_ton_metrics_use_same_apps(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT app_name FROM position_history ORDER BY app_name")
        ph_apps = set(row[0] for row in c.fetchall())

        c.execute("SELECT DISTINCT app_id FROM ton_metrics ORDER BY app_id")
        ton_apps = set(row[0] for row in c.fetchall())

        assert ph_apps == ton_apps

    def test_dates_are_consecutive(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT date FROM position_history ORDER BY date")
        dates = sorted([row[0] for row in c.fetchall()])

        for i in range(len(dates) - 1):
            d1 = datetime.strptime(dates[i], "%Y-%m-%d")
            d2 = datetime.strptime(dates[i + 1], "%Y-%m-%d")
            assert (d2 - d1).days == 1

    def test_contract_address_format(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT contract_address FROM ton_metrics LIMIT 10")
        addresses = [row[0] for row in c.fetchall()]
        assert all(addr.startswith("EQ") for addr in addresses)
        assert all(len(addr) >= 40 for addr in addresses)

    def test_categories_assigned(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT category FROM position_history")
        categories = {row[0] for row in c.fetchall()}
        assert len(categories) >= 5
        assert "Games" in categories

    def test_channel_stats_for_top_apps(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM channel_stats")
        count = c.fetchone()[0]
        assert count > 0

    def test_total_records_scale(self, db_conn):
        """Verify we have ~7000 position_history records (1000 apps x 7 days)."""
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM position_history")
        count = c.fetchone()[0]
        assert count >= 6000

    def test_app_names_unique_per_date(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("""
            SELECT app_name, date, COUNT(*) as cnt
            FROM position_history
            GROUP BY app_name, date
            HAVING cnt > 1
        """)
        duplicates = c.fetchall()
        assert len(duplicates) == 0

    def test_revenue_tiers_vary(self, db_conn):
        """Top apps should have higher revenue than tail apps."""
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT AVG(daily_revenue_ton) FROM ton_metrics WHERE app_id IN (SELECT app_name FROM position_history WHERE position <= 20 AND date = (SELECT MAX(date) FROM position_history))")
        top_avg = c.fetchone()[0]

        c.execute("SELECT AVG(daily_revenue_ton) FROM ton_metrics WHERE app_id IN (SELECT app_name FROM position_history WHERE position > 500 AND date = (SELECT MAX(date) FROM position_history))")
        tail_avg = c.fetchone()[0]

        assert top_avg > tail_avg


class TestGenerateAppName:
    def test_generates_unique_names(self):
        rng = random.Random(42)
        names = set()
        for _ in range(1000):
            name = seed_mock_data._generate_app_name(0, rng)
            names.add(name)
        assert len(names) >= 900

    def test_names_are_reasonable_length(self):
        rng = random.Random(42)
        for _ in range(100):
            name = seed_mock_data._generate_app_name(0, rng)
            assert 3 <= len(name) <= 40


class TestGenerateDescription:
    def test_returns_non_empty(self):
        rng = random.Random(42)
        for cat in seed_mock_data.CATEGORIES:
            desc = seed_mock_data._generate_description("TestApp", cat, rng)
            assert len(desc) > 10
