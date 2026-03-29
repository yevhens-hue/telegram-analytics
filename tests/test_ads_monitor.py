"""Tests for ads_monitor.py — environment-dependent behavior."""
import os
import random
import pytest
from unittest.mock import patch

import ads_monitor


class TestSimulateAdTracking:
    def test_aborts_in_production_by_default(self, monkeypatch, caplog):
        monkeypatch.setattr(ads_monitor, "ENV", "production")
        monkeypatch.delenv("ALLOW_ADS_SIMULATION", raising=False)

        ads_monitor.simulate_ad_tracking()
        assert "Симуляция рекламных данных запрещена" in caplog.text

    def test_runs_in_production_with_flag(self, db_conn, monkeypatch):
        monkeypatch.setattr(ads_monitor, "ENV", "production")
        monkeypatch.setenv("ALLOW_ADS_SIMULATION", "1")

        ads_monitor.simulate_ad_tracking()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM ad_campaigns")
        count = c.fetchone()[0]
        assert count == 5

    def test_runs_in_development(self, db_conn, monkeypatch):
        monkeypatch.setattr(ads_monitor, "ENV", "development")

        ads_monitor.simulate_ad_tracking()

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM ad_campaigns")
        count = c.fetchone()[0]
        assert count == 5

    def test_generates_correct_apps(self, db_conn, monkeypatch):
        monkeypatch.setattr(ads_monitor, "ENV", "development")
        random.seed(42)

        ads_monitor.simulate_ad_tracking()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT app_name FROM ad_campaigns ORDER BY app_name")
        apps = [row[0] for row in c.fetchall()]
        assert apps == ["Blum", "Catizen", "Hamster Kombat", "Notcoin", "Yescoin"]

    def test_budget_in_range(self, db_conn, monkeypatch):
        monkeypatch.setattr(ads_monitor, "ENV", "development")
        random.seed(42)

        ads_monitor.simulate_ad_tracking()

        c = db_conn.cursor()
        c.execute("SELECT estimated_budget FROM ad_campaigns")
        for row in c.fetchall():
            assert 5000 <= row[0] <= 20000

    def test_all_active(self, db_conn, monkeypatch):
        monkeypatch.setattr(ads_monitor, "ENV", "development")

        ads_monitor.simulate_ad_tracking()

        c = db_conn.cursor()
        c.execute("SELECT DISTINCT status FROM ad_campaigns")
        statuses = [row[0] for row in c.fetchall()]
        assert statuses == ["ACTIVE"]
