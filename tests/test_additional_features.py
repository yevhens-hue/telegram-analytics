"""Tests for additional features — watchlist, CSV export, wallet analysis."""
import pytest
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection


# --- Watchlist Tests ---

class TestWatchlist:
    def test_add_to_watchlist(self, db_conn):
        c = db_conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                app_name TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, app_name)
            )
        """)
        c.execute("INSERT INTO user_watchlist (user_id, app_name) VALUES (?, ?)", ("default", "AppA"))
        db_conn.commit()

        c.execute("SELECT app_name FROM user_watchlist WHERE user_id = 'default'")
        apps = [r[0] for r in c.fetchall()]
        assert "AppA" in apps

    def test_watchlist_no_duplicates(self, db_conn):
        c = db_conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                app_name TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, app_name)
            )
        """)
        c.execute("INSERT INTO user_watchlist (user_id, app_name) VALUES (?, ?)", ("default", "AppA"))
        db_conn.commit()

        with pytest.raises(Exception):
            c.execute("INSERT INTO user_watchlist (user_id, app_name) VALUES (?, ?)", ("default", "AppA"))
            db_conn.commit()

    def test_remove_from_watchlist(self, db_conn):
        c = db_conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                app_name TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, app_name)
            )
        """)
        c.execute("INSERT INTO user_watchlist (user_id, app_name) VALUES (?, ?)", ("default", "AppA"))
        db_conn.commit()

        c.execute("DELETE FROM user_watchlist WHERE user_id = ? AND app_name = ?", ("default", "AppA"))
        db_conn.commit()

        c.execute("SELECT COUNT(*) FROM user_watchlist WHERE user_id = 'default'")
        assert c.fetchone()[0] == 0


# --- CSV Export Tests ---

class TestCSVExport:
    def test_export_apps_to_csv(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau) VALUES (?, ?, ?, ?, ?, ?)",
                  ("AppA", today, 1, 5, 1000.0, 50000))
        db_conn.commit()

        c.execute("SELECT app_name, position, growth, revenue_ton, dau FROM app_analytics WHERE date = ?", (today,))
        rows = c.fetchall()

        import io, csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["app_name", "position", "growth", "revenue_ton", "dau"])
        writer.writerows(rows)
        csv_content = output.getvalue()

        assert "app_name" in csv_content
        assert "AppA" in csv_content
        assert "1000" in csv_content


# --- Wallet Analysis Tests ---

class TestWalletAnalysis:
    def test_calculate_total_dau(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, dau) VALUES (?, ?, ?, ?)",
                  ("AppA", today, 1, 50000))
        c.execute("INSERT INTO app_analytics (app_name, date, position, dau) VALUES (?, ?, ?, ?)",
                  ("AppB", today, 2, 30000))
        db_conn.commit()

        c.execute("SELECT SUM(dau) FROM app_analytics WHERE date = ?", (today,))
        total = c.fetchone()[0]
        assert total == 80000

    def test_calculate_total_revenue(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        c = db_conn.cursor()
        c.execute("INSERT INTO app_analytics (app_name, date, position, revenue_ton) VALUES (?, ?, ?, ?)",
                  ("AppA", today, 1, 1000.0))
        c.execute("INSERT INTO app_analytics (app_name, date, position, revenue_ton) VALUES (?, ?, ?, ?)",
                  ("AppB", today, 2, 500.0))
        db_conn.commit()

        c.execute("SELECT SUM(revenue_ton) FROM app_analytics WHERE date = ?", (today,))
        total = c.fetchone()[0]
        assert total == 1500.0

    def test_wallet_distribution_from_ton_metrics(self, db_conn):
        today = datetime.now().strftime("%Y-%m-%d")
        c = db_conn.cursor()
        c.execute("INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES (?, ?, ?, ?, ?)",
                  ("AppA", "EQTest", 1000.0, 5000, today))
        c.execute("INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES (?, ?, ?, ?, ?)",
                  ("AppB", "EQTest2", 500.0, 3000, today))
        db_conn.commit()

        c.execute("SELECT app_id, daily_active_wallets FROM ton_metrics WHERE date = ? ORDER BY daily_active_wallets DESC", (today,))
        rows = c.fetchall()
        assert rows[0][1] == 5000
        assert rows[1][1] == 3000
