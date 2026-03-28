#!/bin/bash

# Telegram Mini Apps Analytics Pipeline
# ------------------------------------

set -e

echo "🚀 Starting Telegram Analytics Pipeline..."

# 0. Init database tables
echo "0/6 Initializing database schema..."
python3 -c "from db_utils import init_all_tables; init_all_tables()"

# 1. Scrape TApps Leaderboard
echo "1/6 Scraping TApps Marketplace..."
python3 tapps_scraper.py

# 2. Deep TON Indexing (Revenue/DAU)
echo "2/6 Indexing TON Blockchain Assets..."
python3 ton_indexer.py

# 3. TG Social Monitoring (Engagement/ERR)
echo "3/6 Monitoring Social Engagement..."
python3 tg_channel_monitor.py

# 4. Ads Tracking (Marketing Influence)
echo "4/6 Tracking Ad Campaigns..."
python3 ads_monitor.py

# 5. AI Analytics Engine (Final Merge & Predictions)
echo "5/6 Running AI Analytics Engine & Forecasting..."
python3 analytics_engine.py

# 6. Run Alerts
echo "6/6 Checking for Alpha Alerts..."
python3 alert_bot.py

echo "✅ Pipeline complete. Dashboard updated."
