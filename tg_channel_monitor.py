import requests
from bs4 import BeautifulSoup
import re
import logging
import time
from db_utils import init_all_tables, save_channel_stats
from config import CONFIG

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF = 2


def _request_with_retry(url, timeout=10):
    for attempt in range(MAX_RETRIES):
        try:
            return requests.get(url, timeout=timeout)
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF ** attempt
                logger.warning("Повтор запроса через %ds (попытка %d/%d): %s", wait, attempt + 1, MAX_RETRIES, e)
                time.sleep(wait)
            else:
                raise
    return None


def parse_views_count(view_str: str) -> int:
    if not view_str:
        return 0

    view_str = view_str.lower().strip().replace(",", "")

    if "k" in view_str:
        try:
            return int(float(view_str.replace("k", "")) * 1000)
        except ValueError:
            return 0

    if "m" in view_str:
        try:
            return int(float(view_str.replace("m", "")) * 1000000)
        except ValueError:
            return 0

    digits = re.sub(r"\D", "", view_str)
    if not digits:
        return 0
    return int(digits)


def scrape_channel(handle: str):
    url = f"https://t.me/s/{handle}"
    logger.info("Парсинг TG канала: %s", url)
    subs = 0
    avg_views = 0
    err = 0

    try:
        response = _request_with_retry(url)
        if response.status_code != 200:
            logger.error("HTTP %d для %s", response.status_code, handle)
            return None

        soup = BeautifulSoup(response.text, "lxml")

        counters = soup.find_all("div", class_="tgme_channel_info_counter")
        for c in counters:
            type_span = c.find("span", class_="counter_type")
            if type_span and "subscriber" in type_span.text.lower():
                val_span = c.find("span", class_="counter_value")
                if val_span:
                    subs = parse_views_count(val_span.text)
                    break

        if subs == 0:
            header_count = soup.find("div", class_="tgme_header_counter")
            if header_count:
                match = re.search(r"([\d\.,kkm]+)\s*sub", header_count.text.lower())
                if match:
                    subs = parse_views_count(match.group(1))

        views_elements = soup.find_all("span", class_="tgme_widget_message_views")
        if not views_elements:
            logger.warning("Не найдены элементы просмотров для %s.", handle)
        else:
            views_list = [parse_views_count(v.text) for v in views_elements if v.text][-20:]
            avg_views = int(sum(views_list) / len(views_list)) if views_list else 0
            err = (avg_views / subs * 100) if subs > 0 else 0

        return subs, avg_views, err

    except Exception as e:
        logger.error("Ошибка парсинга %s: %s", handle, e)
        return None


def monitor_channels():
    init_all_tables()
    channels = CONFIG.get("tg_channels", {})

    for app, handle in channels.items():
        data = scrape_channel(handle)
        if data:
            subs, avg_views, engagement_rate = data
            logger.info("[%s] Подписчики: %d | Ср. просмотры: %d | ERR: %.1f%%", app, subs, avg_views, engagement_rate)
            save_channel_stats(app, handle, subs, avg_views, engagement_rate)
        time.sleep(1)
    logger.info("Мониторинг каналов завершён.")


if __name__ == "__main__":
    monitor_channels()
