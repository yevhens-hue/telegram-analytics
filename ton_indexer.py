import requests
import os
import time
import logging
from db_utils import init_all_tables, save_ton_metrics

logger = logging.getLogger(__name__)

TONAPI_URL = "https://tonapi.io/v2"
TONAPI_KEY = os.environ.get("TONAPI_KEY", "")

APP_CONTRACTS = {
    "Catizen": "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME",
    "Notcoin": "EQDs6p5X2VfOPhQEqSrkpSrkpSrkpSrkpSrkpSrkpSrkyP6A",
}


def analyze_revenue(address: str):
    if len(address) < 40:
        logger.warning("Неверный формат адреса: %s", address)
        return 0, 0

    total_inflow = 0
    unique_senders = set()
    yesterday_ts = int(time.time() - (24 * 3600))

    before_lt = None
    limit = 50

    headers = {}
    if TONAPI_KEY:
        headers["Authorization"] = f"Bearer {TONAPI_KEY}"

    logger.info("Сканирование событий для %s...", address)

    for page in range(5):
        url = f"{TONAPI_URL}/accounts/{address}/events?limit={limit}"
        if before_lt:
            url += f"&before_lt={before_lt}"

        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                logger.error("TonAPI ошибка %d: %s", response.status_code, response.text[:200])
                break

            data = response.json()
            events = data.get("events", [])
            if not events:
                break

            for event in events:
                if event.get("timestamp", 0) < yesterday_ts:
                    return total_inflow / 1e9, len(unique_senders)

                for action in event.get("actions", []):
                    if action.get("type") == "TonTransfer":
                        tx = action.get("TonTransfer", {})
                        recipient = tx.get("recipient", {})
                        sender = tx.get("sender", {})
                        if recipient.get("address") == address:
                            total_inflow += int(tx.get("amount", 0))
                            if sender.get("address"):
                                unique_senders.add(sender["address"])

                before_lt = event.get("lt", 0)

            time.sleep(1)

        except requests.exceptions.RequestException as e:
            logger.error("Ошибка запроса к TonAPI (страница %d): %s", page, e)
            break

    return total_inflow / 1e9, len(unique_senders)


if __name__ == "__main__":
    init_all_tables()

    if not TONAPI_KEY:
        logger.warning("TONAPI_KEY не задан. Используется бесплатный тариф с ограничениями. Задайте переменную окружения TONAPI_KEY.")

    for app_name, address in APP_CONTRACTS.items():
        logger.info("Обработка %s...", app_name)
        revenue, dau = analyze_revenue(address)
        logger.info("  -> Результат: %.2f TON | %d DAU", revenue, dau)
        save_ton_metrics(app_name, address, revenue, dau)

    logger.info("Индексация метрик завершена.")
