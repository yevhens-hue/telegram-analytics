import os
import sys
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

from db_utils import init_all_tables
from tapps_scraper import scrape_tapps_center
from ton_indexer import run_indexing
from tg_channel_monitor import monitor_channels
from ads_monitor import simulate_ad_tracking
from analytics_engine import run_analytics_cycle
from alert_bot import run_alerts
from market_data import fetch_ton_price
from rate_alerts import run_rate_alerts
from backtesting import run_backtest
from reports import generate_weekly_report

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ready"}).encode())

    def log_message(self, format, *args):
        pass


def run_health_server(port):
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server listening on port {port}")
    server.serve_forever()


def _run_in_thread(func, name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if asyncio.iscoroutinefunction(func):
            loop.run_until_complete(func())
        else:
            func()
    except Exception as e:
        logger.error("[%s] Ошибка: %s", name, e, exc_info=True)
        raise
    finally:
        loop.close()


async def run_pipeline():
    logger.info("🚀 Starting Telegram Analytics Pipeline...")

    try:
        logger.info("[1/10] Initializing database schema...")
        init_all_tables()

        logger.info("[2/10] Fetching current TON market price...")
        fetch_ton_price()

        logger.info("[3/10] Scraping TApps Marketplace...")
        apps_data = await scrape_tapps_center()
        with open("tapps_data.json", "w", encoding="utf-8") as f:
            json.dump(apps_data, f, ensure_ascii=False, indent=2)

        logger.info("[4/10] Indexing TON + Monitoring Social (parallel)...")
        loop = asyncio.get_event_loop()
        await asyncio.gather(
            loop.run_in_executor(None, run_indexing),
            loop.run_in_executor(None, monitor_channels),
        )

        logger.info("[5/10] Tracking Ad Campaigns...")
        simulate_ad_tracking()

        logger.info("[6/10] Running AI Analytics Engine...")
        run_analytics_cycle()

        logger.info("[7/10] Checking for Alpha Alerts...")
        run_alerts()

        logger.info("[8/10] Running Rate-of-Change Alerts...")
        run_rate_alerts()

        logger.info("[9/10] Running Prediction Backtesting...")
        run_backtest()

        logger.info("[10/10] Generating Analytics Report...")
        report = generate_weekly_report()
        if report:
            logger.info("\n" + report)
        else:
            logger.info("No report generated (insufficient data).")

        logger.info("[10/10] Done.")

        logger.info("✅ Pipeline complete. Data updated in analytics.db")

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}", exc_info=True)
        sys.exit(1)


def main():
    port = os.environ.get("PORT")
    if port:
        threading.Thread(target=run_health_server, args=(int(port),), daemon=True).start()

    asyncio.run(run_pipeline())

    if port:
        logger.info("Pipeline finished. Staying alive for health checks (Cloud Run mode)...")

    sys.exit(0)


if __name__ == "__main__":
    main()
