import random
import os
import logging
from db_utils import init_all_tables, save_ad_campaigns
from config import CONFIG

logger = logging.getLogger(__name__)

ENV = os.environ.get("APP_ENV", "development")


def simulate_ad_tracking():
    if ENV == "production" and os.environ.get("ALLOW_ADS_SIMULATION") != "1":
        logger.error("Симуляция рекламных данных запрещена в продакшене! Установите APP_ENV=development для тестов.")
        return

    top_apps = CONFIG.get("top_apps", ["Catizen", "Hamster Kombat", "Notcoin", "Blum", "Yescoin"])

    records = []
    for app in top_apps:
        budget = random.uniform(5000, 20000)
        records.append({
            "app_name": app,
            "platform": "Adsgram",
            "estimated_budget": budget,
            "status": "ACTIVE",
        })

    save_ad_campaigns(records)
    logger.info("Рекламные кампании отслежены для %d приложений (РЕЖИМ СИМУЛЯЦИИ).", len(top_apps))


if __name__ == "__main__":
    init_all_tables()
    simulate_ad_tracking()
