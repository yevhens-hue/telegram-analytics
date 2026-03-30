import requests
import logging
from datetime import datetime
from db_utils import get_connection, get_placeholder, save_price_snapshot

logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
TON_ID = "the-open-network"

def fetch_ton_price():
    """
    Fetches the current TON price in USD from CoinGecko.
    """
    try:
        params = {
            "ids": TON_ID,
            "vs_currencies": "usd"
        }
        response = requests.get(COINGECKO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get(TON_ID, {}).get("usd", 0)

        if price > 0:
            logger.info("Current TON price: $%.2f", price)
            _save_price(price)
            save_price_snapshot("TON", price, "daily")
            return price
        else:
            logger.warning("Failed to parse TON price from response.")
            return None
    except Exception as e:
        logger.error("Error fetching TON price: %s", e)
        return None

def _save_price(price):
    """
    Saves the price to the database for historical tracking.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    p = get_placeholder()

    with get_connection() as conn:
        c = conn.cursor()
        # Initialize prices table if not exists (or add to init_all_tables later)
        c.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT,
                price_usd REAL,
                date TEXT,
                UNIQUE(asset_id, date)
            )
        """)

        c.execute(f"""
            INSERT INTO market_data (asset_id, price_usd, date)
            VALUES ({p}, {p}, {p})
            ON CONFLICT(asset_id, date) DO UPDATE SET price_usd=excluded.price_usd
        """, ("TON", price, today))

def get_latest_ton_price():
    """
    Returns the latest available TON price from the database.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT price_usd FROM market_data WHERE asset_id = 'TON' ORDER BY date DESC LIMIT 1")
        res = c.fetchone()
        return res[0] if res else None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_ton_price()
