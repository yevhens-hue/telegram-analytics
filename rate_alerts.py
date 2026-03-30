import os
import logging
from datetime import datetime, timedelta
from db_utils import get_connection, get_placeholder
from alert_bot import _send_telegram

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")

DEFAULT_THRESHOLDS = {
    "revenue_change_pct": 200,
    "dau_change_pct": 200,
    "growth_change_abs": 10,
    "trend_score_change_pct": 150,
}


def detect_rate_changes(thresholds=None):
    """
    Detect sudden metric changes compared to the previous day.
    Returns list of alerts.
    """
    thresholds = thresholds or DEFAULT_THRESHOLDS
    p = get_placeholder()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    alerts = []

    with get_connection() as conn:
        c = conn.cursor()

        c.execute(f"SELECT app_name, position, growth, revenue_ton, dau, trend_score FROM app_analytics WHERE date = {p}", (today,))
        today_data = {row[0]: row[1:] for row in c.fetchall()}

        c.execute(f"SELECT app_name, position, growth, revenue_ton, dau, trend_score FROM app_analytics WHERE date = {p}", (yesterday,))
        yesterday_data = {row[0]: row[1:] for row in c.fetchall()}

        for app_name, metrics in today_data.items():
            pos, growth, revenue, dau, trend = metrics
            if app_name not in yesterday_data:
                continue

            prev_metrics = yesterday_data[app_name]
            prev_pos, prev_growth, prev_revenue, prev_dau, prev_trend = prev_metrics

            if prev_revenue > 0:
                rev_change = ((revenue - prev_revenue) / prev_revenue) * 100
                if abs(rev_change) >= thresholds["revenue_change_pct"]:
                    direction = "📈" if rev_change > 0 else "📉"
                    alerts.append({
                        "app_name": app_name,
                        "metric": "revenue_ton",
                        "message": f"{direction} {app_name}: доход изменился на {rev_change:+.0f}% ({prev_revenue:.0f} → {revenue:.0f} TON)",
                        "severity": "high" if abs(rev_change) >= 500 else "medium",
                    })

            if prev_dau > 0:
                dau_change = ((dau - prev_dau) / prev_dau) * 100
                if abs(dau_change) >= thresholds["dau_change_pct"]:
                    direction = "📈" if dau_change > 0 else "📉"
                    alerts.append({
                        "app_name": app_name,
                        "metric": "dau",
                        "message": f"{direction} {app_name}: DAU изменился на {dau_change:+.0f}% ({prev_dau:,} → {dau:,})",
                        "severity": "high" if abs(dau_change) >= 500 else "medium",
                    })

            if prev_trend > 0:
                trend_change = ((trend - prev_trend) / prev_trend) * 100
                if abs(trend_change) >= thresholds["trend_score_change_pct"]:
                    alerts.append({
                        "app_name": app_name,
                        "metric": "trend_score",
                        "message": f"🔥 {app_name}: trend score изменился на {trend_change:+.0f}% ({prev_trend:.1f} → {trend:.1f})",
                        "severity": "medium",
                    })

            growth_diff = abs(growth - prev_growth)
            if growth_diff >= thresholds["growth_change_abs"]:
                alerts.append({
                    "app_name": app_name,
                    "metric": "growth",
                    "message": f"⚡ {app_name}: рост изменился на {growth_diff:.0f} позиций (было {prev_growth:+d}, стало {growth:+d})",
                    "severity": "high" if growth_diff >= 20 else "medium",
                })

    return alerts


def run_rate_alerts():
    """Detect and send rate-of-change alerts."""
    alerts = detect_rate_changes()

    if not alerts:
        logger.info("Нет аномальных изменений метрик.")
        return []

    logger.info("Обнаружено %d алертов по аномальным изменениям.", len(alerts))

    for alert in alerts:
        logger.info("  [%s] %s", alert["severity"], alert["message"])
        if BOT_TOKEN and CHAT_ID:
            _send_telegram(f"🚨 *Rate Alert*\n{alert['message']}")

    today = datetime.now().strftime("%Y-%m-%d")
    from db_utils import get_connection, get_placeholder as _gp
    p = _gp()
    with get_connection() as conn:
        c = conn.cursor()
        for alert in alerts:
            c.execute(
                f"INSERT INTO alert_history (app_name, message, date, status) VALUES ({p}, {p}, {p}, {p})",
                (alert["app_name"], alert["message"], today, f"rate_alert:{alert['severity']}"),
            )

    return alerts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = run_rate_alerts()
    for r in results:
        print(r["message"])


def get_significant_changes(threshold=10):
    """
    Detect significant position changes from position_history.
    Returns list of dicts with app_name, jump, prev_pos, curr_pos.
    """
    p = get_placeholder()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    changes = []
    with get_connection() as conn:
        c = conn.cursor()

        c.execute(f"SELECT app_name, position FROM position_history WHERE date = {p}", (today,))
        today_positions = {row[0]: row[1] for row in c.fetchall()}

        c.execute(f"SELECT app_name, position FROM position_history WHERE date = {p}", (yesterday,))
        yesterday_positions = {row[0]: row[1] for row in c.fetchall()}

        for app_name, curr_pos in today_positions.items():
            if app_name in yesterday_positions:
                prev_pos = yesterday_positions[app_name]
                jump = abs(prev_pos - curr_pos)
                if jump >= threshold:
                    changes.append({
                        "app_name": app_name,
                        "prev_pos": prev_pos,
                        "curr_pos": curr_pos,
                        "jump": jump,
                    })

    return changes
