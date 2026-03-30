import requests
import os
import logging
from datetime import datetime
from db_utils import get_connection, get_placeholder

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")


def get_alpha_signals():
    today = datetime.now().strftime("%Y-%m-%d")
    p = get_placeholder()

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"""
            SELECT app_name, growth, trend_score, organic_index, prediction_7d, market_sentiment
            FROM app_analytics
            WHERE date = {p} AND trend_score > 5
            ORDER BY trend_score DESC
            LIMIT 5
            """,
            (today,),
        )
        return c.fetchall()


def format_alert(signal):
    name, growth, trend, organic, pred, sentiment = signal
    emoji = "🚀" if growth > 5 else "🔥"

    msg = f"{emoji} *{name}*\n"
    msg += f"📈 Growth: +{growth} | "
    msg += f"📊 Trend: {trend:.1f} | "
    msg += f"🧠 7D: #{pred} | "
    msg += f"💡 Organic: {organic:.0f}% | "
    msg += f"🎭 Sentiment: {sentiment:.0f}/100"
    return msg


def run_alerts():
    signals = get_alpha_signals()
    if not signals:
        logger.info("Нет значимых альфа-сигналов на сегодня.")
        return

    logger.info("Обнаружено %d альфа-сигналов.", len(signals))

    for sig in signals:
        text = format_alert(sig)
        logger.info("---\n%s", text)
        status = "sent" if (BOT_TOKEN and CHAT_ID) else "logged"
        
        if status == "sent":
             _send_telegram(text)
             
        _save_alert_history(sig[0], text, status)

def _save_alert_history(app_name, message, status):
    today = datetime.now().strftime("%Y-%m-%d")
    p = get_placeholder()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"INSERT INTO alert_history (app_name, message, date, status) VALUES ({p}, {p}, {p}, {p})",
            (app_name, message, today, status)
        )


def _send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        if resp.status_code != 200:
            logger.error("Ошибка отправки в Telegram: %d", resp.status_code)
    except requests.exceptions.RequestException as e:
        logger.error("Ошибка запроса к Telegram API: %s", e)


if __name__ == "__main__":
    run_alerts()
    logger.info("Проверка алертов завершена.")
