# Architecture

## Data Flow

```
tapps_scraper.py ──┐
ton_indexer.py ────┤
tg_channel_monitor.py ─┤
ads_monitor.py ────┘
        │
        ▼
   analytics.db / Postgres
        │
        ▼
analytics_engine.py ──→ app_analytics + analytics_history
        │
        ▼
   alert_bot.py ──→ Telegram notifications
        │
        ▼
   dashboard (Next.js) ──→ / , /top-charts, /ton-indexer
```

## Pipeline Steps

| Step | Module | Type | Parallel? |
|------|--------|------|-----------|
| 0 | `db_utils.init_all_tables()` | DB init | No |
| 1 | `tapps_scraper.scrape_tapps_center()` | Async scraper | No |
| 2 | `ton_indexer.run_indexing()` | Sync API calls | Yes (with step 3) |
| 3 | `tg_channel_monitor.monitor_channels()` | Sync HTTP | Yes (with step 2) |
| 4 | `ads_monitor.simulate_ad_tracking()` | Sync simulation | No |
| 5 | `analytics_engine.run_analytics_cycle()` | Sync DB | No |
| 6 | `alert_bot.run_alerts()` | Sync API | No |

Steps 2 and 3 run in parallel via `asyncio.gather()`.

## Configuration

Configuration is loaded in `config.py` with this priority:
1. Environment variables (`TON_CONTRACTS`, `TG_CHANNELS` as JSON)
2. `config.json` file
3. Built-in defaults in `_DEFAULT_CONFIG`

## Key Formulas

- **organic_index** = `(100/position) + (growth * 2.5) + (err * 2) - (ad_spend/1000)`, clamped to [5, 100]
- **trend_score** = `(growth * 12) + (revenue / 50) + (err * 5)`, normalized to [0, 100]
- **market_sentiment** = `(err * 8) + (growth * 5) + 50`, clamped to [0, 100]
- **prediction_7d** = `max(1, position - growth * 0.7)`

## Retry Logic

External API calls (TonAPI, Telegram channel scraping) use exponential backoff:
- Max 3 retries
- Backoff: 1s, 2s, 4s
