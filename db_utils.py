import sqlite3
import os
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DB_FILE = os.environ.get("ANALYTICS_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics.db"))


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        logger.error("Ошибка БД: %s", e)
        raise
    finally:
        conn.close()


def init_all_tables():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS position_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                description TEXT,
                category TEXT,
                position INTEGER,
                date TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS ad_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                platform TEXT,
                estimated_budget REAL,
                status TEXT,
                date TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS channel_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                handle TEXT,
                subscribers INTEGER,
                avg_views INTEGER,
                err REAL,
                date TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS ton_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT,
                contract_address TEXT,
                daily_revenue_ton REAL,
                daily_active_wallets INTEGER,
                date TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS app_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                date TEXT,
                position INTEGER,
                growth INTEGER,
                revenue_ton REAL,
                dau INTEGER,
                organic_index REAL,
                trend_score REAL,
                ad_spend_est REAL DEFAULT 0,
                is_mock INTEGER DEFAULT 0,
                market_sentiment REAL DEFAULT 50,
                prediction_7d INTEGER,
                UNIQUE(app_name, date)
            )
        """)

        # Миграция: добавляем недостающие колонки если таблица уже существует
        c.execute("PRAGMA table_info(app_analytics)")
        columns = {col[1] for col in c.fetchall()}
        if "is_mock" not in columns:
            c.execute("ALTER TABLE app_analytics ADD COLUMN is_mock INTEGER DEFAULT 0")
        if "market_sentiment" not in columns:
            c.execute("ALTER TABLE app_analytics ADD COLUMN market_sentiment REAL DEFAULT 50")
        if "prediction_7d" not in columns:
            c.execute("ALTER TABLE app_analytics ADD COLUMN prediction_7d INTEGER")

    logger.info("Все таблицы инициализированы.")


def save_position_history(apps, date=None):
    # type: (list[dict], Optional[str]) -> None
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as conn:
        c = conn.cursor()
        for app in apps:
            c.execute(
                "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                (app["name"], app.get("description", ""), app.get("category", ""), app["position"], date),
            )
    logger.info("Сохранено %d записей в position_history.", len(apps))


def save_ad_campaigns(records, date=None):
    # type: (list[dict], Optional[str]) -> None
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as conn:
        c = conn.cursor()
        for rec in records:
            c.execute(
                "INSERT INTO ad_campaigns (app_name, platform, estimated_budget, status, date) VALUES (?, ?, ?, ?, ?)",
                (rec["app_name"], rec["platform"], rec["estimated_budget"], rec["status"], date),
            )
    logger.info("Сохранено %d рекламных кампаний.", len(records))


def save_channel_stats(app_name, handle, subs, avg_views, err, date=None):
    # type: (str, str, int, int, float, Optional[str]) -> None
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO channel_stats (app_name, handle, subscribers, avg_views, err, date) VALUES (?, ?, ?, ?, ?, ?)",
            (app_name, handle, subs, avg_views, err, date),
        )
    logger.info("Канал %s: %d подписчиков, %d средних просмотров.", handle, subs, avg_views)


def save_ton_metrics(app_name, address, revenue, dau, date=None):
    # type: (str, str, float, int, Optional[str]) -> None
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES (?, ?, ?, ?, ?)",
            (app_name, address, revenue, dau, date),
        )
    logger.info("TON метрики для %s: %.2f TON, %d DAU.", app_name, revenue, dau)


def save_app_analytics(record):
    # type: (dict) -> None
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO app_analytics (
                app_name, date, position, growth, revenue_ton, dau,
                organic_index, trend_score, ad_spend_est, is_mock,
                market_sentiment, prediction_7d
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(app_name, date) DO UPDATE SET
                position=excluded.position,
                growth=excluded.growth,
                revenue_ton=excluded.revenue_ton,
                dau=excluded.dau,
                organic_index=excluded.organic_index,
                trend_score=excluded.trend_score,
                ad_spend_est=excluded.ad_spend_est,
                is_mock=excluded.is_mock,
                market_sentiment=excluded.market_sentiment,
                prediction_7d=excluded.prediction_7d
            """,
            (
                record["app_name"],
                record["date"],
                record["position"],
                record["growth"],
                record["revenue_ton"],
                record["dau"],
                record["organic_index"],
                record["trend_score"],
                record.get("ad_spend_est", 0),
                record.get("is_mock", 0),
                record.get("market_sentiment", 50),
                record.get("prediction_7d"),
            ),
        )
