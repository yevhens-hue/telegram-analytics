import asyncio
import logging
from tapps_scraper import scrape_tapps_center

logging.basicConfig(level=logging.INFO)

async def test_scraper_scale():
    apps = await scrape_tapps_center()
    print(f"\n🚀 Total apps scraped: {len(apps)}")
    if len(apps) >= 900:
        print("✅ Scale-up successful!")
    else:
        print("⚠️ Still fewer apps than expected.")
    
    # Optional assert step
    assert len(apps) >= 900, f"Scraped {len(apps)} applications, expected at least 900 (full market)"

if __name__ == "__main__":
    asyncio.run(test_scraper_scale())
