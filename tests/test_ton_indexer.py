"""Tests for ton_indexer.py — revenue analysis with mocked API."""
import time
import pytest
from unittest.mock import patch, MagicMock
import requests

import ton_indexer


class TestAnalyzeRevenue:
    """Tests for analyze_revenue with mocked HTTP responses."""

    def test_short_address_returns_zero(self):
        result = ton_indexer.analyze_revenue("short")
        assert result == (0, 0)

    def test_empty_address_returns_zero(self):
        result = ton_indexer.analyze_revenue("")
        assert result == (0, 0)

    @patch("ton_indexer.time.sleep")
    @patch("ton_indexer.requests.get")
    def test_sums_ton_transfers_single_page(self, mock_get, mock_sleep):
        """Should sum incoming TON transfers and count unique senders."""
        target_addr = "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME"
        now = int(time.time())
        old_ts = now - (48 * 3600)  # 48 hours ago — old event triggers return

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "events": [
                {
                    "timestamp": now - 3600,
                    "lt": 200,
                    "actions": [
                        {
                            "type": "TonTransfer",
                            "TonTransfer": {
                                "recipient": {"address": target_addr},
                                "sender": {"address": "EQSender1"},
                                "amount": "1000000000",
                            },
                        },
                        {
                            "type": "TonTransfer",
                            "TonTransfer": {
                                "recipient": {"address": target_addr},
                                "sender": {"address": "EQSender2"},
                                "amount": "2000000000",
                            },
                        },
                        {
                            "type": "TonTransfer",
                            "TonTransfer": {
                                "recipient": {"address": "EQOtherAddr"},
                                "sender": {"address": "EQSender3"},
                                "amount": "5000000000",
                            },
                        },
                    ],
                },
                {
                    "timestamp": old_ts,
                    "lt": 100,
                    "actions": [],
                },
            ]
        }
        mock_get.return_value = mock_response

        revenue, dau = ton_indexer.analyze_revenue(target_addr)
        assert revenue == 3.0  # 1 + 2 TON (third is to different addr, old event triggers return)
        assert dau == 2  # Two unique senders

    @patch("ton_indexer.time.sleep")
    @patch("ton_indexer.requests.get")
    def test_stops_on_old_events(self, mock_get, mock_sleep):
        """Should stop processing when events are older than 24h."""
        target_addr = "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME"
        old_ts = int(time.time()) - (48 * 3600)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "events": [
                {
                    "timestamp": old_ts,
                    "lt": 100,
                    "actions": [],
                },
            ]
        }
        mock_get.return_value = mock_response

        revenue, dau = ton_indexer.analyze_revenue(target_addr)
        mock_get.assert_called_once()
        assert revenue == 0
        assert dau == 0

    @patch("ton_indexer.time.sleep")
    @patch("ton_indexer.requests.get")
    def test_handles_api_error(self, mock_get, mock_sleep):
        """Should gracefully handle HTTP errors."""
        target_addr = "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME"

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limited"
        mock_get.return_value = mock_response

        revenue, dau = ton_indexer.analyze_revenue(target_addr)
        assert revenue == 0
        assert dau == 0

    @patch("ton_indexer.time.sleep")
    @patch("ton_indexer.requests.get")
    def test_handles_empty_events(self, mock_get, mock_sleep):
        """Should return zero when no events found."""
        target_addr = "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"events": []}
        mock_get.return_value = mock_response

        revenue, dau = ton_indexer.analyze_revenue(target_addr)
        assert revenue == 0
        assert dau == 0

    @patch("ton_indexer.time.sleep")
    @patch("ton_indexer.requests.get")
    def test_handles_request_exception(self, mock_get, mock_sleep):
        """Should handle connection errors gracefully."""
        target_addr = "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME"
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        revenue, dau = ton_indexer.analyze_revenue(target_addr)
        assert revenue == 0
        assert dau == 0

    @patch("ton_indexer.time.sleep")
    @patch("ton_indexer.requests.get")
    def test_paginates_through_events(self, mock_get, mock_sleep):
        """Should follow pagination cursor across pages."""
        target_addr = "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME"
        now = int(time.time())

        call_count = [0]

        def side_effect(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            call_count[0] += 1

            if call_count[0] == 1:
                # First page: one recent event with lt=200
                resp.json.return_value = {
                    "events": [
                        {
                            "timestamp": now - 3600,
                            "lt": 200,
                            "actions": [
                                {
                                    "type": "TonTransfer",
                                    "TonTransfer": {
                                        "recipient": {"address": target_addr},
                                        "sender": {"address": "EQPage1"},
                                        "amount": "1000000000",
                                    },
                                },
                            ],
                        },
                    ]
                }
            else:
                # Second page: one recent event (processed) then one old event (triggers return)
                resp.json.return_value = {
                    "events": [
                        {
                            "timestamp": now - 7200,
                            "lt": 150,
                            "actions": [
                                {
                                    "type": "TonTransfer",
                                    "TonTransfer": {
                                        "recipient": {"address": target_addr},
                                        "sender": {"address": "EQPage2"},
                                        "amount": "2000000000",
                                    },
                                },
                            ],
                        },
                        {
                            "timestamp": now - (48 * 3600),  # Old — triggers early return
                            "lt": 100,
                            "actions": [],
                        },
                    ]
                }
            return resp

        mock_get.side_effect = side_effect

        revenue, dau = ton_indexer.analyze_revenue(target_addr)
        # Page 1: 1 TON (lt=200), Page 2: 2 TON (lt=150 processed), then old event returns
        assert revenue == 3.0
        assert dau == 2
        assert mock_get.call_count == 2


class TestRunIndexing:
    @patch("ton_indexer.save_ton_metrics")
    @patch("ton_indexer.analyze_revenue")
    @patch("ton_indexer.init_all_tables")
    def test_calls_analyze_for_each_app(self, mock_init, mock_analyze, mock_save):
        mock_analyze.return_value = (100.0, 50)

        ton_indexer.run_indexing()

        mock_init.assert_called_once()
        from config import CONFIG
        contracts = CONFIG.get("ton_contracts", {})
        assert mock_analyze.call_count == len(contracts)
        assert mock_save.call_count == len(contracts)
