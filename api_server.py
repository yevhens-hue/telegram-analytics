import logging
from datetime import datetime, timedelta
from typing import Optional
from db_utils import get_connection, get_placeholder

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException, Query
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    logger.warning("FastAPI не установлен. REST API недоступен. Установите: pip install fastapi uvicorn")


def create_app():
    if not HAS_FASTAPI:
        raise RuntimeError("FastAPI required: pip install fastapi uvicorn")

    app = FastAPI(title="Telegram Analytics API", version="1.0.0")

    @app.get("/api/apps")
    def list_apps(date: Optional[str] = None, limit: int = Query(default=50, le=200)):
        p = get_placeholder()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT app_name, position, growth, revenue_ton, dau, organic_index, trend_score, market_sentiment, prediction_7d FROM app_analytics WHERE date = {p} ORDER BY position ASC LIMIT {limit}",
                (date,),
            )
            columns = ["app_name", "position", "growth", "revenue_ton", "dau", "organic_index", "trend_score", "market_sentiment", "prediction_7d"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        return {"date": date, "apps": rows}

    @app.get("/api/apps/{app_name}")
    def get_app(app_name: str, days: int = Query(default=30, le=365)):
        p = get_placeholder()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT date, position, growth, revenue_ton, dau, organic_index, trend_score, market_sentiment, prediction_7d FROM app_analytics WHERE app_name = {p} AND date >= {p} ORDER BY date DESC",
                (app_name, cutoff),
            )
            columns = ["date", "position", "growth", "revenue_ton", "dau", "organic_index", "trend_score", "market_sentiment", "prediction_7d"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        if not rows:
            raise HTTPException(status_code=404, detail=f"App '{app_name}' not found")
        return {"app_name": app_name, "history": rows}

    @app.get("/api/signals")
    def get_signals(date: Optional[str] = None, min_trend: float = Query(default=5.0, ge=0)):
        p = get_placeholder()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT app_name, growth, trend_score, organic_index, prediction_7d, market_sentiment FROM app_analytics WHERE date = {p} AND trend_score >= {p} ORDER BY trend_score DESC",
                (date, min_trend),
            )
            columns = ["app_name", "growth", "trend_score", "organic_index", "prediction_7d", "market_sentiment"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        return {"date": date, "signals": rows}

    @app.get("/api/alerts")
    def get_alerts(date: Optional[str] = None, limit: int = Query(default=50, le=200)):
        p = get_placeholder()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT app_name, message, date, status FROM alert_history WHERE date = {p} ORDER BY id DESC LIMIT {limit}",
                (date,),
            )
            columns = ["app_name", "message", "date", "status"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        return {"date": date, "alerts": rows}

    @app.get("/api/trend")
    def get_trend(days: int = Query(default=30, le=365)):
        p = get_placeholder()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT date, SUM(revenue_ton) as total_ton, SUM(dau) as total_dau, COUNT(*) as app_count FROM app_analytics WHERE date >= {p} GROUP BY date ORDER BY date ASC",
                (cutoff,),
            )
            columns = ["date", "total_ton", "total_dau", "app_count"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        return {"trend": rows}

    @app.get("/api/market")
    def get_market_price(asset: str = "TON", days: int = Query(default=30, le=365)):
        p = get_placeholder()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT price_usd, timestamp FROM price_history WHERE asset_id = {p} AND timestamp >= {p} ORDER BY timestamp ASC",
                (asset, cutoff),
            )
            columns = ["price_usd", "timestamp"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        return {"asset": asset, "history": rows}

    @app.get("/api/social/{app_name}")
    def get_social_mentions(app_name: str, days: int = Query(default=30, le=365)):
        p = get_placeholder()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT platform, content, sentiment_score, date FROM social_mentions WHERE app_name = {p} AND date >= {p} ORDER BY date DESC",
                (app_name, cutoff),
            )
            columns = ["platform", "content", "sentiment_score", "date"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        return {"app_name": app_name, "mentions": rows}

    @app.get("/api/backtest")
    def get_backtest_results(limit: int = Query(default=10, le=50)):
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT run_date, period_days, total_predictions, direction_accuracy_pct, avg_position_error FROM backtest_results ORDER BY id DESC LIMIT {limit}",
            )
            columns = ["run_date", "period_days", "total_predictions", "direction_accuracy_pct", "avg_position_error"]
            rows = [dict(zip(columns, row)) for row in c.fetchall()]
        return {"backtests": rows}

    @app.get("/api/health")
    def health_check():
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    return app


def run_api_server(host="0.0.0.0", port=8000):
    if not HAS_FASTAPI:
        logger.error("FastAPI не установлен.")
        return
    import uvicorn
    app = create_app()
    logger.info("Запуск REST API на %s:%d", host, port)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_api_server()
