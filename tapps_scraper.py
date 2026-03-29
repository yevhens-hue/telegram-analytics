import asyncio
from playwright.async_api import async_playwright
import json
import logging
from db_utils import init_all_tables, save_position_history

logger = logging.getLogger(__name__)


async def scrape_tapps_center():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            logger.error("Не удалось запустить браузер: %s", e)
            return []

        page = await browser.new_page()
        logger.info("Переход на tapps.center...")
        try:
            await page.goto("https://tapps.center/", wait_until="networkidle", timeout=30000)
        except Exception as e:
            logger.error("Ошибка загрузки страницы: %s", e)
            await browser.close()
            return []

        try:
            await page.wait_for_selector("[class*='applicationCard']", timeout=10000)
        except Exception as e:
            logger.warning("Селектор не найден, пробуем альтернативный подход. Ошибка: %s", e)

        for _ in range(3):
            await page.keyboard.press("PageDown")
            await asyncio.sleep(1)

        apps_data = await page.evaluate("""() => {
            const apps = [];

            // Стратегия 1: ищем по частичному совпадению класса (устойчивее к хешам)
            let cards = document.querySelectorAll('[class*="applicationCardLink"]');
            if (!cards.length) {
                // Стратегия 2: ищем ссылки на /app/
                cards = document.querySelectorAll('a[href*="/app/"]');
            }
            if (!cards.length) {
                // Стратегия 3: ищем карточки по структуре
                cards = document.querySelectorAll('[class*="applicationCard"]');
            }

            cards.forEach((card, index) => {
                // Гибкий поиск имени приложения
                const nameEl = card.querySelector('[class*="title"]')
                    || card.querySelector('h3')
                    || card.querySelector('h2')
                    || card.querySelector('[class*="name"]');
                const descEl = card.querySelector('[class*="description"]')
                    || card.querySelector('[class*="desc"]')
                    || card.querySelector('p');

                if (nameEl) {
                    apps.push({
                        name: nameEl.textContent.trim(),
                        description: descEl ? descEl.textContent.trim() : "",
                        category: "Trending",
                        position: index + 1
                    });
                }
            });
            return apps;
        }""")

        await browser.close()
        return apps_data


if __name__ == "__main__":
    init_all_tables()
    result = asyncio.run(scrape_tapps_center())
    with open("tapps_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    save_position_history(result)
    logger.info("Парсинг завершён, данные в tapps_data.json и analytics.db")
