import asyncio
from playwright.async_api import async_playwright
import json
import logging
from db_utils import init_all_tables, save_position_history

logger = logging.getLogger(__name__)


CATEGORIES = [
    "trending",
    "games",
    "socialandlifestyle",
    "payments",
    "finance",
    "nft",
    "tools",
    "playtoearn",
    "other",
    "new"
]


async def _scroll_to_bottom(page, max_scrolls=30):
    """Scroll down repeatedly to trigger lazy loading."""
    prev_height = 0
    for i in range(max_scrolls):
        await page.keyboard.press("End")
        await asyncio.sleep(0.8)
        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height


async def _extract_apps(page):
    """Extract app data from the current page DOM."""
    return await page.evaluate("""() => {
        const apps = [];
        const seen = new Set();

        // Try multiple selector strategies
        const cardSets = [
            document.querySelectorAll('div[class*="applicationCardLink"]'),
            document.querySelectorAll('a[href*="/app/"]'),
            document.querySelectorAll('a[href*="/application/"]'),
            document.querySelectorAll('[class*="applicationCard"]'),
        ];

        for (const cards of cardSets) {
            for (const card of cards) {
                let name = "";
                const titleEl = card.querySelector('[class*="title"]') || card.querySelector('h3') || card.querySelector('h2') || card.querySelector('[class*="name"]');
                if (titleEl) {
                    name = titleEl.innerText.trim();
                } else {
                    const text = card.innerText.split('\\n').filter(l => l.trim().length > 1 && l.trim().length < 80);
                    if (text.length > 0) name = text[0].trim();
                }

                if (!name || name.length < 2 || name.length > 100 || name === 'OPEN' || seen.has(name)) continue;
                seen.add(name);

                const descEl = card.querySelector('[class*="description"]') || card.querySelector('[class*="desc"]') || card.querySelector('p');
                const href = card.getAttribute('href') || '';

                apps.push({
                    name: name,
                    description: descEl ? descEl.innerText.trim() : "",
                    href: href
                });
            }
        }
        return apps;
    }""")


async def scrape_tapps_center():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            logger.error("Не удалось запустить браузер: %s", e)
            return []

        page = await browser.new_page()
        all_apps = []
        seen_apps = set()

        urls_to_visit = [f"https://tapps.center/{cat}" for cat in CATEGORIES]

        for url in urls_to_visit:
            category_name = url.split("/")[-1].capitalize() if url != "https://tapps.center/" else "Trending"
            logger.info("Парсинг %s (категория: %s)...", url, category_name)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Try clicking "Load More" / "Show All" buttons
                for _ in range(10):
                    try:
                        load_more = await page.query_selector('button:has-text("Load More"), button:has-text("Show More"), button:has-text("See All"), [class*="loadMore"], [class*="showMore"]')
                        if load_more and await load_more.is_visible():
                            await load_more.click()
                            await asyncio.sleep(1.5)
                        else:
                            break
                    except Exception:
                        break

                await _scroll_to_bottom(page, max_scrolls=20)

                apps_on_page = await _extract_apps(page)
                logger.info("  Найдено %d приложений на %s", len(apps_on_page), url)

                new_count = 0
                for app in apps_on_page:
                    if app['name'] not in seen_apps:
                        seen_apps.add(app['name'])
                        all_apps.append({
                            "name": app["name"],
                            "description": app.get("description", ""),
                            "category": category_name,
                            "position": len(all_apps) + 1,
                        })
                        new_count += 1

                logger.info("  +%d новых (всего: %d)", new_count, len(all_apps))

            except Exception as e:
                logger.error("Ошибка при парсинге %s: %s", url, e)

        await browser.close()
        logger.info("Итого собрано %d уникальных приложений.", len(all_apps))
        return all_apps


if __name__ == "__main__":
    init_all_tables()
    result = asyncio.run(scrape_tapps_center())
    with open("tapps_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    save_position_history(result)
    logger.info("Парсинг завершён, данные в tapps_data.json и analytics.db")
