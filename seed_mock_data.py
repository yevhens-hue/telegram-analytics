import random
import logging
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection

logger = logging.getLogger(__name__)


def init_mock_data():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM position_history")
        if c.fetchone()[0] > 0:
            logger.info("Данные уже существуют, пропуск заполнения моками.")
            return

        apps = [
            ("Catizen", "Where Every Game Leads to an Airdrop", "Games"),
            ("Hamster Kombat", "A crypto game on telegram", "Games"),
            ("Wallet", "Get up to 5% on TON!", "Finance"),
            ("Synaptizy", "Train your brain and get TON!", "Games"),
            ("BingoTon", "Free Bingo. Win Real TON Every Week.", "Games"),
        ]

        today = datetime.now()

        for i in range(7):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            for idx, app in enumerate(apps):
                pos = idx + 1 + random.randint(-1, 2)
                if pos < 1:
                    pos = 1
                c.execute(
                    "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                    (app[0], app[1], app[2], pos, date_str),
                )

                revenue = random.uniform(500, 5000) * (len(apps) - idx)
                dau = int(revenue * random.uniform(5, 15))
                c.execute(
                    "INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES (?, ?, ?, ?, ?)",
                    (app[0], "EQ...", revenue, dau, date_str),
                )

    logger.info("Моковые данные успешно добавлены.")


if __name__ == "__main__":
    init_all_tables()
    init_mock_data()
