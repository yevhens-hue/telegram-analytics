#!/bin/bash

# Telegram Mini Apps Analytics Pipeline
# ------------------------------------

set -e

echo "🚀 Starting Telegram Analytics Unified Pipeline..."

# Run the full pipeline via main.py
python3 main.py

echo "✅ Pipeline complete. Data updated in analytics.db"
