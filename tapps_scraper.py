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

        # Build URLs
        urls_to_visit = [f"https://tapps.center/{cat}" for cat in CATEGORIES]




        for url in urls_to_visit:
            logger.info("Парсинг %s...", url)
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Scroll to load more
                for _ in range(5):
                    await page.keyboard.press("PageDown")
                    await asyncio.sleep(1)

                apps_on_page = await page.evaluate("""() => {
                    const apps = [];
                    // Handle both Trending (hompage) and Category page structures
                    // Category pages use div.styles_applicationCardLink__...
                    // Some might use a tags. Let's be generic.
                    
                    const cards = Array.from(document.querySelectorAll('div[class*="applicationCardLink"], a[href*="/app/"], a[href*="/application/"]'));
                    
                    cards.forEach((card) => {
                        let name = "";
                        const titleEl = card.querySelector('[class*="title"]') || card.querySelector('h3') || card.querySelector('h2');
                        if (titleEl) {
                            name = titleEl.innerText.trim();
                        } else {
                            // Fallback to card text
                            name = card.innerText.split('\\n')[0].trim();
                        }
                        
                        if (name && name.length > 1 && name.length < 100 && name !== 'OPEN') {
                            const descEl = card.querySelector('[class*="description"]') || card.querySelector('p');
                            apps.push({
                                name: name,
                                description: descEl ? descEl.innerText.trim() : ""
                            });
                        }
                    });
                    return apps;
                }""")
                
                logger.info("  Найдено %d потенциальных приложений на %s", len(apps_on_page), url)

                for app in apps_on_page:
                    if app['name'] not in seen_apps:
                        seen_apps.add(app['name'])
                        all_apps.append({
                            **app,
                            "category": "Trending" if url == "https://tapps.center/" else url.split("/")[-1].capitalize(),
                            "position": len(all_apps) + 1
                        })
                
                logger.info("  Найдено %d новых приложений на %s (всего: %d)", len(apps_on_page), url, len(all_apps))

            except Exception as e:
                logger.error("Ошибка при парсинге %s: %s", url, e)

        await browser.close()
        return all_apps


if __name__ == "__main__":
    init_all_tables()
    result = asyncio.run(scrape_tapps_center())
    with open("tapps_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    save_position_history(result)
    logger.info("Парсинг завершён, данные в tapps_data.json и analytics.db")
