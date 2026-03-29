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

    def test_seeds_ton_metrics(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM ton_metrics")
        count = c.fetchone()[0]
        assert count > 0

    def test_creates_7_days_of_data(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT date FROM position_history")
        dates = [row[0] for row in c.fetchall()]
        assert len(dates) == 7

    def test_seeds_all_apps(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT app_name FROM position_history ORDER BY app_name")
        apps = [row[0] for row in c.fetchall()]
        assert "Catizen" in apps
        assert "Hamster Kombat" in apps
        assert "Wallet" in apps
        assert "Synaptizy" in apps
        assert "BingoTon" in apps

    def test_skips_if_data_exists(self, db_conn, caplog):
        import logging
        seed_mock_data.init_mock_data()
        # Run again — should skip
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

    def test_contract_address_is_placeholder(self, db_conn):
        seed_mock_data.init_mock_data()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT contract_address FROM ton_metrics")
        addresses = [row[0] for row in c.fetchall()]
        assert all(addr.startswith("EQ") for addr in addresses)
