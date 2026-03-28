# 🚀 Telegram Mini Apps (TMA) Analytics Platform

A professional-grade analytics & forecasting platform for the Telegram Mini Apps ecosystem. It combines on-chain TON indexing, social engagement monitoring (ERR), ad tracking, and AI-driven trend projections.

## ✨ Features
- **Deep TON Indexing**: Real-time revenue (TON) and DAU tracking via blockchain events.
- **Social Pulse**: Automated monitoring of Telegram announcement channels for engagement rate (ERR).
- **Ad Monitoring**: Tracking marketing reach and "Paid vs Organic" growth indices.
- **AI Analytics Engine**: 7-day rank forecasting and market sentiment scoring.
- **Alpha Bot**: Telegram bot notifications for breakout signals and high-confidence "Alpha" projects.
- **Premium Dashboard**: High-performance dashboard built with Next.js, Framer Motion, and Tailwind CSS.

## 🛠 Tech Stack
- **Backend/Analytics**: Python (Playwright, BeautifulSoup, SQLite)
- **Frontend**: Next.js 15+, TypeScript, Tailwind CSS, Lucide Icons, Framer Motion
- **Database**: SQLite (optimized for high-frequency writes)
- **Blockchain**: TON API / Web3 indexing

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
cd dashboard && npm install
```

### 2. Run Analytics Pipeline
Run the unified script to scrape, index, monitor, and compute AI analytics:
```bash
./run_all.sh
```

### 3. Launch Dashboard
```bash
cd dashboard
npm run dev
```

## 📊 Analytics Methodology
- **Organic Index**: Calculated by comparing position growth speed against estimated ad spend and social engagement. High index (>80%) indicates viral viral growth.
- **AI Prediction**: Linear projection with decay factors, predicting position moves for the next 7 days.
- **Trend Score**: A combined metric of growth velocity, revenue volume, and engagement pulse.

## 📜 License
MIT
