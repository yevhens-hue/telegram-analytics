import random as _random_module
import logging
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection, get_placeholder, save_analytics_history
from config import CONFIG

logger = logging.getLogger(__name__)

_mock_rng = _random_module.Random(42)

TREND_SCORE_CAP = CONFIG.get("trend_score_cap", 200)


def _normalize_trend_score(raw_score, cap=TREND_SCORE_CAP):
    return min(100, max(0, (raw_score / cap) * 100))


def run_analytics_cycle():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday_dt = datetime.now() - timedelta(days=1)
    yesterday = yesterday_dt.strftime("%Y-%m-%d")
    p = get_placeholder()

    with get_connection() as conn:
        c = conn.cursor()

        c.execute(f"SELECT app_name, position, category FROM position_history WHERE date = {p}", (today,))
        current_apps = c.fetchall()

        if not current_apps:
            logger.warning("Нет данных за сегодня (%s). Сначала запустите парсеры.", today)
            return

        for app_name, pos, cat in current_apps:
            is_mock = 0

            c.execute(f"SELECT position FROM position_history WHERE app_name = {p} AND date = {p}", (app_name, yesterday))
            prev_res = c.fetchone()
            prev_pos = prev_res[0] if prev_res else pos
            growth = prev_pos - pos

            c.execute(f"SELECT daily_revenue_ton, daily_active_wallets FROM ton_metrics WHERE app_id = {p} AND date = {p}", (app_name, today))
            ton_res = c.fetchone()

            raw_revenue = ton_res[0] if ton_res else 0
            raw_dau = ton_res[1] if ton_res else 0

            if raw_revenue > 0:
                revenue = raw_revenue
            else:
                revenue = _mock_rng.uniform(500, 5000) if pos < 10 else _mock_rng.uniform(10, 200)
                is_mock = 1

            if raw_dau > 0:
                dau = raw_dau
            else:
                dau = _mock_rng.randint(50000, 500000) if pos < 10 else _mock_rng.randint(100, 2000)
                is_mock = 1

            c.execute(f"SELECT err FROM channel_stats WHERE app_name = {p} AND date = {p}", (app_name, today))
            err_res = c.fetchone()
            engagement_rate = err_res[0] if err_res else 0

            c.execute(f"SELECT estimated_budget FROM ad_campaigns WHERE app_name = {p} AND date = {p}", (app_name, today))
            ad_res = c.fetchone()
            ad_spend = ad_res[0] if ad_res else 0

            err_bonus = engagement_rate * 2
            marketing_penalty = ad_spend / 1000

            base_org = (100 / max(1, pos)) + (growth * 2.5)
            organic_index = min(100, max(5, base_org + err_bonus - marketing_penalty))

            raw_trend = (growth * 12) + (revenue / 50) + (engagement_rate * 5)
            trend_score = _normalize_trend_score(raw_trend)

            sentiment_score = min(100, max(0, (engagement_rate * 8) + (growth * 5) + 50))

            projected_rank = max(1, int(pos - (growth * 0.7)))

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
                (app_name, today, pos, growth, revenue, dau,
                 organic_index, trend_score, ad_spend, is_mock,
                 sentiment_score, projected_rank),
            )

            save_analytics_history(app_name, today, {
                "organic_index": organic_index,
                "trend_score": trend_score,
                "market_sentiment": sentiment_score,
                "revenue_ton": revenue,
                "dau": dau,
            }, cursor=c)

            data_type = "моковые" if is_mock else "реальные"
            logger.info("[%s] %s данные — позиция: %d, рост: %d, доход: %.0f TON, сентимент: %.0f",
                        app_name, data_type, pos, growth, revenue, sentiment_score)

    logger.info("Глубокая аналитика рассчитана для %d приложений.", len(current_apps))


if __name__ == "__main__":
    init_all_tables()
    run_analytics_cycle()
