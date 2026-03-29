import sqlite3
import os
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Any, Union

logger = logging.getLogger(__name__)

DB_FILE = os.environ.get("ANALYTICS_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics.db"))
POSTGRES_URL = os.environ.get("POSTGRES_URL")


def _get_psycopg2():
    try:
        import psycopg2
        return psycopg2
    except ImportError:
        raise ImportError(
            "psycopg2 is required for Postgres. Install it: pip install psycopg2-binary"
        )


@contextmanager
def get_connection():
    if POSTGRES_URL:
        psycopg2 = _get_psycopg2()
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Ошибка Postgres: %s", e)
            raise
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error("Ошибка SQLite: %s", e)
            raise
        finally:
            conn.close()


def get_placeholder():
    return "%s" if POSTGRES_URL else "?"


def _validate_required(record, fields):
    for field in fields:
        if field not in record or record[field] is None:
            raise ValueError(f"Обязательное поле '{field}' отсутствует или равно None")


def _validate_positive(value, field):
    if value is not None and value < 0:
        raise ValueError(f"Поле '{field}' должно быть >= 0, получено {value}")


def init_all_tables():
    with get_connection() as conn:
        c = conn.cursor()

        serial_type = "SERIAL PRIMARY KEY" if POSTGRES_URL else "INTEGER PRIMARY KEY AUTOINCREMENT"

        c.execute(f"""
            CREATE TABLE IF NOT EXISTS position_history (
                id {serial_type},
                app_name TEXT,
                description TEXT,
                category TEXT,
                position INTEGER,
                date TEXT
            )
        """)

        c.execute(f"""
            CREATE TABLE IF NOT EXISTS ad_campaigns (
                id {serial_type},
                app_name TEXT,
                platform TEXT,
                estimated_budget REAL,
                status TEXT,
                date TEXT
            )
        """)

        c.execute(f"""
            CREATE TABLE IF NOT EXISTS channel_stats (
                id {serial_type},
                app_name TEXT,
                handle TEXT,
                subscribers INTEGER,
                avg_views INTEGER,
                err REAL,
                date TEXT
            )
        """)

        c.execute(f"""
            CREATE TABLE IF NOT EXISTS ton_metrics (
                id {serial_type},
                app_id TEXT,
                contract_address TEXT,
                daily_revenue_ton REAL,
                daily_active_wallets INTEGER,
                date TEXT
            )
        """)

        c.execute(f"""
            CREATE TABLE IF NOT EXISTS app_analytics (
                id {serial_type},
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

        c.execute(f"""
            CREATE TABLE IF NOT EXISTS analytics_history (
                id {serial_type},
                app_name TEXT,
                date TEXT,
                metric_name TEXT,
                metric_value REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_position_history_date ON position_history(date)",
            "CREATE INDEX IF NOT EXISTS idx_position_history_app_date ON position_history(app_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_app_analytics_date ON app_analytics(date)",
            "CREATE INDEX IF NOT EXISTS idx_app_analytics_trend ON app_analytics(trend_score)",
            "CREATE INDEX IF NOT EXISTS idx_app_analytics_app_date ON app_analytics(app_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_ton_metrics_app_date ON ton_metrics(app_id, date)",
            "CREATE INDEX IF NOT EXISTS idx_ton_metrics_date ON ton_metrics(date)",
            "CREATE INDEX IF NOT EXISTS idx_channel_stats_app_date ON channel_stats(app_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_ad_campaigns_app_date ON ad_campaigns(app_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_history_app_date ON analytics_history(app_name, date)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_history_metric ON analytics_history(metric_name)",
        ]

        for idx_sql in indexes:
            try:
                c.execute(idx_sql)
            except Exception:
                pass

        if not POSTGRES_URL:
            c.execute("PRAGMA table_info(app_analytics)")
            columns = {col[1] for col in c.fetchall()}
            if "is_mock" not in columns:
                c.execute("ALTER TABLE app_analytics ADD COLUMN is_mock INTEGER DEFAULT 0")
            if "market_sentiment" not in columns:
                c.execute("ALTER TABLE app_analytics ADD COLUMN market_sentiment REAL DEFAULT 50")
            if "prediction_7d" not in columns:
                c.execute("ALTER TABLE app_analytics ADD COLUMN prediction_7d INTEGER")

    logger.info("Все таблицы и индексы инициализированы.")


def save_position_history(apps, date=None):
    if not apps:
        return
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    for app in apps:
        _validate_required(app, ["name", "position"])
        _validate_positive(app["position"], "position")

    p = get_placeholder()
    with get_connection() as conn:
        c = conn.cursor()
        rows = [
            (app["name"], app.get("description", ""), app.get("category", ""), app["position"], date)
            for app in apps
        ]
        c.executemany(
            f"INSERT INTO position_history (app_name, description, category, position, date) VALUES ({p}, {p}, {p}, {p}, {p})",
            rows,
        )
    logger.info("Сохранено %d записей в position_history.", len(apps))


def save_ad_campaigns(records, date=None):
    if not records:
        return
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    for rec in records:
        _validate_required(rec, ["app_name", "platform", "status"])
        _validate_positive(rec.get("estimated_budget"), "estimated_budget")

    p = get_placeholder()
    with get_connection() as conn:
        c = conn.cursor()
        rows = [
            (rec["app_name"], rec["platform"], rec.get("estimated_budget", 0), rec["status"], date)
            for rec in records
        ]
        c.executemany(
            f"INSERT INTO ad_campaigns (app_name, platform, estimated_budget, status, date) VALUES ({p}, {p}, {p}, {p}, {p})",
            rows,
        )
    logger.info("Сохранено %d рекламных кампаний.", len(records))


def save_channel_stats(app_name, handle, subs, avg_views, err, date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    _validate_positive(subs, "subscribers")
    _validate_positive(avg_views, "avg_views")

    p = get_placeholder()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"INSERT INTO channel_stats (app_name, handle, subscribers, avg_views, err, date) VALUES ({p}, {p}, {p}, {p}, {p}, {p})",
            (app_name, handle, subs, avg_views, err, date),
        )
    logger.info("Канал %s: %d подписчиков, %d средних просмотров.", handle, subs, avg_views)


def save_ton_metrics(app_name, address, revenue, dau, date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    _validate_positive(revenue, "revenue")
    _validate_positive(dau, "dau")

    p = get_placeholder()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES ({p}, {p}, {p}, {p}, {p})",
            (app_name, address, revenue, dau, date),
        )
    logger.info("TON метрики для %s: %.2f TON, %d DAU.", app_name, revenue, dau)


def save_app_analytics(record):
    _validate_required(record, ["app_name", "date", "position"])

    p = get_placeholder()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"""
            INSERT INTO app_analytics (
                app_name, date, position, growth, revenue_ton, dau,
                organic_index, trend_score, ad_spend_est, is_mock,
                market_sentiment, prediction_7d
            )
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
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
                record.get("growth", 0),
                record.get("revenue_ton", 0),
                record.get("dau", 0),
                record.get("organic_index", 0),
                record.get("trend_score", 0),
                record.get("ad_spend_est", 0),
                record.get("is_mock", 0),
                record.get("market_sentiment", 50),
                record.get("prediction_7d"),
            ),
        )


def save_analytics_history(app_name, date, metrics, cursor=None):
    if not metrics:
        return

    p = get_placeholder()
    rows = [
        (app_name, date, name, value)
        for name, value in metrics.items()
    ]

    if cursor:
        cursor.executemany(
            f"INSERT INTO analytics_history (app_name, date, metric_name, metric_value) VALUES ({p}, {p}, {p}, {p})",
            rows,
        )
    else:
        with get_connection() as conn:
            c = conn.cursor()
            c.executemany(
                f"INSERT INTO analytics_history (app_name, date, metric_name, metric_value) VALUES ({p}, {p}, {p}, {p})",
                rows,
            )
