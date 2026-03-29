"""Tests for tg_channel_monitor.py — parsing and scraping."""
import pytest
from unittest.mock import patch, MagicMock

import tg_channel_monitor


class TestParseViewsCount:
    """Tests for the pure function parse_views_count."""

    def test_plain_number(self):
        assert tg_channel_monitor.parse_views_count("1234") == 1234

    def test_number_with_commas(self):
        assert tg_channel_monitor.parse_views_count("1,234") == 1234

    def test_number_with_spaces(self):
        assert tg_channel_monitor.parse_views_count("12 345") == 12345

    def test_k_suffix_integer(self):
        assert tg_channel_monitor.parse_views_count("12k") == 12000

    def test_k_suffix_decimal(self):
        assert tg_channel_monitor.parse_views_count("1.2k") == 1200

    def test_k_suffix_case_insensitive(self):
        assert tg_channel_monitor.parse_views_count("5K") == 5000

    def test_m_suffix_integer(self):
        assert tg_channel_monitor.parse_views_count("2m") == 2000000

    def test_m_suffix_decimal(self):
        assert tg_channel_monitor.parse_views_count("1.5m") == 1500000

    def test_empty_string(self):
        assert tg_channel_monitor.parse_views_count("") == 0

    def test_none_value(self):
        assert tg_channel_monitor.parse_views_count(None) == 0

    def test_invalid_text(self):
        assert tg_channel_monitor.parse_views_count("abc") == 0

    def test_whitespace_only(self):
        assert tg_channel_monitor.parse_views_count("   ") == 0

    def test_with_leading_spaces(self):
        assert tg_channel_monitor.parse_views_count("  500  ") == 500

    def test_large_number(self):
        assert tg_channel_monitor.parse_views_count("1,500,000") == 1500000


class TestScrapeChannel:
    """Tests for scrape_channel with mocked HTTP responses."""

    SAMPLE_HTML = """
    <html>
    <body>
        <div class="tgme_channel_info_counter">
            <span class="counter_value">100k</span>
            <span class="counter_type">subscribers</span>
        </div>
        <div class="tgme_channel_info_counter">
            <span class="counter_value">500</span>
            <span class="counter_type">posts</span>
        </div>
        <span class="tgme_widget_message_views">10k</span>
        <span class="tgme_widget_message_views">20k</span>
        <span class="tgme_widget_message_views">15k</span>
        <span class="tgme_widget_message_views">5k</span>
    </body>
    </html>
    """

    @patch("tg_channel_monitor.requests.get")
    def test_returns_subs_avg_views_err(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.SAMPLE_HTML
        mock_get.return_value = mock_response

        result = tg_channel_monitor.scrape_channel("test_handle")
        assert result is not None
        subs, avg_views, err = result
        assert subs == 100000
        assert avg_views == 12500  # (10000+20000+15000+5000)/4
        assert err > 0

    @patch("tg_channel_monitor.requests.get")
    def test_returns_none_on_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = tg_channel_monitor.scrape_channel("nonexistent")
        assert result is None

    @patch("tg_channel_monitor.requests.get")
    def test_returns_none_on_exception(self, mock_get):
        mock_get.side_effect = Exception("Connection timeout")

        result = tg_channel_monitor.scrape_channel("test_handle")
        assert result is None

    @patch("tg_channel_monitor.requests.get")
    def test_handles_no_views_elements(self, mock_get):
        html_no_views = """
        <html><body>
            <div class="tgme_channel_info_counter">
                <span class="counter_value">1k</span>
                <span class="counter_type">subscribers</span>
            </div>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html_no_views
        mock_get.return_value = mock_response

        result = tg_channel_monitor.scrape_channel("test_handle")
        assert result is not None
        subs, avg_views, err = result
        assert subs == 1000
        assert avg_views == 0
        assert err == 0

    @patch("tg_channel_monitor.requests.get")
    def test_fallback_to_header_counter(self, mock_get):
        html_header = """
        <html><body>
            <div class="tgme_header_counter">50k subscribers</div>
            <span class="tgme_widget_message_views">1k</span>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html_header
        mock_get.return_value = mock_response

        result = tg_channel_monitor.scrape_channel("test_handle")
        assert result is not None
        subs, _, _ = result
        assert subs == 50000
