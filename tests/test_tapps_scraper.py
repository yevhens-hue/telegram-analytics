"""Tests for tapps_scraper.py — scraping logic with mocked Playwright."""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open

import tapps_scraper


class TestScrapeTappsCenter:
    @pytest.mark.asyncio
    async def test_returns_list_of_apps(self):
        """Should return a list of app dicts from page evaluation."""
        mock_apps = [
            {"name": "App1", "description": "Desc 1", "category": "Trending", "position": 1},
            {"name": "App2", "description": "Desc 2", "category": "Trending", "position": 2},
        ]

        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=mock_apps)
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.keyboard = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_p = MagicMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_context = AsyncMock()
        mock_pw_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_pw_context.__aexit__ = AsyncMock(return_value=None)

        with patch("tapps_scraper.async_playwright", return_value=mock_pw_context):
            result = await tapps_scraper.scrape_tapps_center()

        assert len(result) == 2
        assert result[0]["name"] == "App1"
        assert result[1]["position"] == 2

    @pytest.mark.asyncio
    async def test_empty_result_when_no_cards_found(self):
        """Should return empty list when no app cards found."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=Exception("timeout"))
        mock_page.keyboard = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_p = MagicMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_context = AsyncMock()
        mock_pw_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_pw_context.__aexit__ = AsyncMock(return_value=None)

        with patch("tapps_scraper.async_playwright", return_value=mock_pw_context):
            result = await tapps_scraper.scrape_tapps_center()

        assert result == []

    @pytest.mark.asyncio
    async def test_navigates_to_correct_url(self):
        """Should navigate to tapps.center."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.keyboard = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_p = MagicMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_context = AsyncMock()
        mock_pw_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_pw_context.__aexit__ = AsyncMock(return_value=None)

        with patch("tapps_scraper.async_playwright", return_value=mock_pw_context):
            await tapps_scraper.scrape_tapps_center()

        mock_page.goto.assert_called_once_with("https://tapps.center/", wait_until="networkidle", timeout=30000)

    @pytest.mark.asyncio
    async def test_browser_closed_after_scraping(self):
        """Should always close the browser."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.keyboard = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_p = MagicMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_context = AsyncMock()
        mock_pw_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_pw_context.__aexit__ = AsyncMock(return_value=None)

        with patch("tapps_scraper.async_playwright", return_value=mock_pw_context):
            await tapps_scraper.scrape_tapps_center()

        mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrolls_page_before_evaluating(self):
        """Should press PageDown 3 times to load lazy content."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.keyboard = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_p = MagicMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_context = AsyncMock()
        mock_pw_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_pw_context.__aexit__ = AsyncMock(return_value=None)

        with patch("tapps_scraper.async_playwright", return_value=mock_pw_context):
            with patch("tapps_scraper.asyncio.sleep", new_callable=AsyncMock):
                await tapps_scraper.scrape_tapps_center()

        assert mock_page.keyboard.press.call_count == 3

    @pytest.mark.asyncio
    async def test_launches_headless_chromium(self):
        """Should launch Chromium in headless mode."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.keyboard = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_p = MagicMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_context = AsyncMock()
        mock_pw_context.__aenter__ = AsyncMock(return_value=mock_p)
        mock_pw_context.__aexit__ = AsyncMock(return_value=None)

        with patch("tapps_scraper.async_playwright", return_value=mock_pw_context):
            await tapps_scraper.scrape_tapps_center()

        mock_p.chromium.launch.assert_called_once_with(headless=True)
