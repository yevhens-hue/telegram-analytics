import requests
import os
import logging
from datetime import datetime
from db_utils import get_connection

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")


def get_alpha_signals():
    today = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT app_name, growth, trend_score, organic_index, prediction_7d, market_sentiment
            FROM app_analytics
            WHERE date = ? AND trend_score > 5
            ORDER BY trend_score DESC
            LIMIT 5
            """,
            (today,),
        )
        return c.fetchall()


def format_alert(signal):
    name, growth, trend, organic, pred, sentiment = signal
    emoji = "🚀" if growth > 5 else "🔥"

    msg = f"{emoji} *ALPHA ALERT: {name}*\n"
    msg += f"📈 Growth: +{growth} positions\n"
    msg += f"📊 Trend Score: {trend:.1f}\n"
    msg += f"🧠 AI Projection: Reach #{pred} in 7d\n"
    msg += f"💡 Organic Confidence: {organic:.0f}%\n"
    msg += f"🎭 Market Sentiment: {sentiment:.0f}/100\n"
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

        if BOT_TOKEN and CHAT_ID:
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
                if resp.status_code != 200:
                    logger.error("Ошибка отправки в Telegram: %d", resp.status_code)
            except requests.exceptions.RequestException as e:
                logger.error("Ошибка запроса к Telegram API: %s", e)


if __name__ == "__main__":
    run_alerts()
    logger.info("Проверка алертов завершена.")
