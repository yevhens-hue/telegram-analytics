import random
import logging
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection

logger = logging.getLogger(__name__)

MOCK_APPS = {
    "Catizen": {"category": "Games", "contract": "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME"},
    "Hamster Kombat": {"category": "Games", "contract": "EQBxkGlumxHaR2ti3MMaExGPKeAXKz7HhJNJt_VJT-NIbRpa"},
    "Notcoin": {"category": "Games", "contract": "EQDs6p5X2VfOPhQEqSrkpSrkpSrkpSrkpSrkpSrkpSrkyP6A"},
    "Blum": {"category": "DeFi", "contract": "EQBl6z6TeyS8cFu_5yK8VUTJWNnFJNnm5DkCfRfKz8G4M2bF"},
    "Wallet": {"category": "Utility", "contract": "EQDKjIu1mkGZwW2FJmRMdQ4YjWbT9yV5R3yL5fzXqG2MZQjA"},
    "Synaptizy": {"category": "Social", "contract": "EQAbCdEfGhIjKlMnOpQrStUvWxYz1234567890AbCdEfGh"},
    "BingoTon": {"category": "Games", "contract": "EQBingoTonContractAddress1234567890AbCdEfGhIjKlMn"},
}

SEED_DAYS = 7


def init_mock_data():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM position_history")
        if c.fetchone()[0] > 0:
            logger.info("Данные уже существуют, пропускаем сидирование.")
            return

        today = datetime.now()

        for i in range(SEED_DAYS):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            for idx, (app_name, info) in enumerate(MOCK_APPS.items()):
                pos = idx + 1 + random.randint(-2, 2)
                pos = max(1, pos)

                c.execute(
                    "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                    (app_name, f"Top {info['category']} app in Telegram", info["category"], pos, date_str),
                )

                revenue = random.uniform(200, 5000)
                dau = int(revenue * random.uniform(10, 50))
                c.execute(
                    "INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES (?, ?, ?, ?, ?)",
                    (app_name, info["contract"], revenue, dau, date_str),
                )

                subs = random.randint(500000, 20000000)
                views = int(subs * random.uniform(0.01, 0.1))
                c.execute(
                    "INSERT INTO channel_stats (app_name, subscribers, avg_views, err, date) VALUES (?, ?, ?, ?, ?)",
                    (app_name, subs, views, 5.2, date_str),
                )

    logger.info("База данных расширена: %d приложений в 4+ категориях проинициализированы.", len(MOCK_APPS))


if __name__ == "__main__":
    init_all_tables()
    init_mock_data()
