import random
import logging
import hashlib
from datetime import datetime, timedelta
from db_utils import init_all_tables, get_connection

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Games", "DeFi", "Social", "Utilities", "NFT", "Finance",
    "Tools", "Entertainment", "Education", "News", "Shopping",
    "Health", "Travel", "Music", "Art", "AI", "Productivity",
]

CATEGORY_WEIGHTS = [25, 12, 10, 15, 8, 8, 6, 5, 3, 2, 2, 1, 1, 1, 1, 1, 1]

APP_PREFIXES = [
    "Crypto", "Ton", "Moon", "Star", "Gold", "Diamond", "Pixel", "Mega",
    "Super", "Ultra", "Turbo", "Alpha", "Beta", "Zen", "Neo", "Pro",
    "Mini", "Max", "Prime", "Elite", "Nano", "Hyper", "DeFi", "Web3",
    "Chain", "Block", "Token", "Swap", "Yield", "Stake", "Farm", "Pool",
    "Guild", "Quest", "Raid", "Clash", "Rush", "Dash", "Blast", "Crush",
    "Tap", "Click", "Spin", "Roll", "Flip", "Jump", "Run", "Race",
]

APP_SUFFIXES = [
    "Arena", "Hub", "Lab", "Verse", "World", "Land", "City", "Empire",
    "Kingdom", "Realm", "Zone", "Club", "DAO", "Fi", "Swap", "Bridge",
    "Wallet", "Pay", "Bot", "AI", "GPT", "X", "3D", "Plus",
    "Pro", "Prime", "Max", "Lite", "Mini", "Go", "IO", "Net",
    "Pets", "Heroes", "Legends", "Wars", "Tycoon", "Manager", "Builder",
    "Maker", "Hunter", "Master", "Champion", "Ninja", "Panda", "Cat",
    "Dog", "Hamster", "Fox", "Bear", "Dragon", "Phoenix", "Unicorn",
]

ADJECTIVES = [
    "Rapid", "Lucky", "Happy", "Brave", "Wild", "Epic", "Royal",
    "Cosmic", "Solar", "Lunar", "Ocean", "Forest", "Thunder", "Fire",
    "Ice", "Dark", "Light", "Magic", "Crystal", "Shadow", "Neon",
]


def _generate_app_name(index, rng):
    """Generate a unique app name based on index."""
    style = rng.randint(0, 4)
    if style == 0:
        return rng.choice(APP_PREFIXES) + rng.choice(APP_SUFFIXES)
    elif style == 1:
        return rng.choice(ADJECTIVES) + rng.choice(APP_SUFFIXES)
    elif style == 2:
        return rng.choice(APP_PREFIXES) + str(rng.randint(1, 99))
    elif style == 3:
        return rng.choice(ADJECTIVES) + rng.choice(APP_PREFIXES)
    else:
        return rng.choice(APP_PREFIXES) + rng.choice(APP_PREFIXES) + rng.choice(APP_SUFFIXES)


def _generate_description(name, category, rng):
    templates = {
        "Games": [
            f"Play-to-earn game on Telegram. {name} brings blockchain gaming to your chat.",
            f"Addictive tap-to-earn experience. Compete with friends in {name}.",
            f"Strategic RPG with NFT rewards. Build your empire in {name}.",
        ],
        "DeFi": [
            f"Decentralized exchange on TON. Swap tokens instantly with {name}.",
            f"Yield farming and staking platform. Earn passive income with {name}.",
            f"Liquidity pools and lending protocol. Maximize your TON returns.",
        ],
        "Social": [
            f"Social network for crypto enthusiasts. Connect through {name}.",
            f"Community-driven platform with token rewards in {name}.",
        ],
        "Utilities": [
            f"Essential utility tool for Telegram users. {name} simplifies your workflow.",
            f"All-in-one toolkit for TON blockchain. Manage assets with {name}.",
        ],
        "NFT": [
            f"NFT marketplace on TON. Discover, buy, and sell digital art.",
            f"Create and trade unique digital collectibles on {name}.",
        ],
        "Finance": [
            f"Financial management tool with crypto integration. Track your portfolio.",
            f"Smart payment solution for Telegram. Send and receive TON easily.",
        ],
        "AI": [
            f"AI-powered assistant for Telegram. {name} helps you work smarter.",
            f"Machine learning tools for crypto trading and analysis.",
        ],
    }
    cat_templates = templates.get(category, [
        f"Innovative {category.lower()} application for Telegram Mini Apps.",
        f"Top-rated {category.lower()} tool in the TON ecosystem.",
    ])
    return rng.choice(cat_templates)


def _generate_contract_address(rng):
    """Generate a realistic-looking TON contract address."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    return "EQ" + "".join(rng.choice(chars) for _ in range(46))


SEED_DAYS = 7
TARGET_APPS = 1000


def init_mock_data():
    rng = random.Random(42)

    with get_connection() as conn:
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM position_history")
        if c.fetchone()[0] > 0:
            logger.info("Данные уже существуют, пропускаем сидирование.")
            return

        today = datetime.now()

        # Generate 1000 unique app names
        used_names = set()
        apps = []
        attempts = 0
        while len(apps) < TARGET_APPS and attempts < TARGET_APPS * 10:
            attempts += 1
            name = _generate_app_name(len(apps), rng)
            if name in used_names or len(name) < 3 or len(name) > 40:
                continue
            used_names.add(name)
            cat_idx = rng.choices(range(len(CATEGORIES)), weights=CATEGORY_WEIGHTS, k=1)[0]
            category = CATEGORIES[cat_idx]
            apps.append({
                "name": name,
                "category": category,
                "description": _generate_description(name, category, rng),
                "contract": _generate_contract_address(rng),
            })

        logger.info("Сгенерировано %d приложений для сидирования.", len(apps))

        # Assign base popularity tiers
        tier_ranges = [
            (0, 20, "whale"),       # Top 20 — massive apps
            (20, 100, "popular"),   # 20-100 — popular
            (100, 300, "growing"),  # 100-300 — growing
            (300, 600, "mid"),      # 300-600 — mid-tier
            (600, 1000, "long"),    # 600-1000 — long tail
        ]

        for day_offset in range(SEED_DAYS):
            date_str = (today - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            rows_ph = []
            rows_ton = []
            rows_cs = []

            for idx, app in enumerate(apps):
                # Position with small daily variance
                base_pos = idx + 1
                pos = max(1, base_pos + rng.randint(-2, 2))

                # Find tier
                tier = "long"
                for start, end, t in tier_ranges:
                    if start <= idx < end:
                        tier = t
                        break

                # Revenue based on tier
                if tier == "whale":
                    revenue = rng.uniform(5000, 50000)
                elif tier == "popular":
                    revenue = rng.uniform(1000, 15000)
                elif tier == "growing":
                    revenue = rng.uniform(200, 5000)
                elif tier == "mid":
                    revenue = rng.uniform(50, 1500)
                else:
                    revenue = rng.uniform(5, 300)

                # DAU correlated with revenue
                dau_multiplier = {"whale": 80, "popular": 50, "growing": 30, "mid": 20, "long": 10}
                dau = int(revenue * rng.uniform(dau_multiplier[tier] * 0.5, dau_multiplier[tier] * 1.5))
                dau = max(10, dau)

                rows_ph.append((
                    app["name"], app["description"], app["category"], pos, date_str,
                ))

                rows_ton.append((
                    app["name"], app["contract"], revenue, dau, date_str,
                ))

                # Channel stats (only for top apps)
                if idx < 300:
                    subs_base = {"whale": 5000000, "popular": 1000000, "growing": 200000, "mid": 50000, "long": 10000}
                    subs = int(subs_base.get(tier, 10000) * rng.uniform(0.3, 3.0))
                    views = int(subs * rng.uniform(0.01, 0.15))
                    err = round(views / subs * 100, 1) if subs > 0 else 0
                    handle = app["name"].lower().replace(" ", "")[:32]
                    rows_cs.append((app["name"], handle, subs, views, err, date_str))

            c.executemany(
                "INSERT INTO position_history (app_name, description, category, position, date) VALUES (?, ?, ?, ?, ?)",
                rows_ph,
            )
            c.executemany(
                "INSERT INTO ton_metrics (app_id, contract_address, daily_revenue_ton, daily_active_wallets, date) VALUES (?, ?, ?, ?, ?)",
                rows_ton,
            )
            if rows_cs:
                c.executemany(
                    "INSERT INTO channel_stats (app_name, handle, subscribers, avg_views, err, date) VALUES (?, ?, ?, ?, ?, ?)",
                    rows_cs,
                )

        logger.info("База данных: %d приложений × %d дней = %d записей.", len(apps), SEED_DAYS, len(apps) * SEED_DAYS)


if __name__ == "__main__":
    init_all_tables()
    init_mock_data()
