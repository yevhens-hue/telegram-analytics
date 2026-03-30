"""Tests for news_sentiment.py — sentiment analysis backends."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import db_utils
from db_utils import init_all_tables, get_connection


class TestKeywordSentiment:
    def test_neutral_text_returns_baseline(self, db_conn):
        from news_sentiment import _keyword_sentiment
        score = _keyword_sentiment("Hello world")
        assert 40 <= score <= 60

    def test_bullish_keywords_increase_score(self, db_conn):
        from news_sentiment import _keyword_sentiment
        score = _keyword_sentiment("Airdrop is coming! Listing confirmed!")
        assert score > 50

    def test_bearish_keywords_decrease_score(self, db_conn):
        from news_sentiment import _keyword_sentiment
        score = _keyword_sentiment("Scam alert! Hack detected! Dump incoming!")
        assert score < 50

    def test_score_bounded_0_100(self, db_conn):
        from news_sentiment import _keyword_sentiment
        very_bearish = _keyword_sentiment("scam scam scam hack dump rug exploit rekt fud bearish sell")
        assert very_bearish >= 0
        very_bullish = _keyword_sentiment(" ".join(["airdrop listing partnership growth buy pump alpha moon bullish gem"] * 5))
        assert very_bullish <= 100

    def test_case_insensitive(self, db_conn):
        from news_sentiment import _keyword_sentiment
        lower = _keyword_sentiment("airdrop listing")
        upper = _keyword_sentiment("AIRDROP LISTING")
        assert lower == upper


class TestAnalyzeChannelSentiment:
    def test_returns_float_between_0_and_100(self, db_conn):
        from news_sentiment import analyze_channel_sentiment
        score = analyze_channel_sentiment("TestChannel", ["Great news!"])
        assert 0 <= score <= 100

    def test_returns_50_when_no_texts(self, db_conn):
        from news_sentiment import analyze_channel_sentiment
        score = analyze_channel_sentiment("TestChannel")
        assert score == 50.0

    def test_saves_social_mention(self, db_conn):
        from news_sentiment import analyze_channel_sentiment
        analyze_channel_sentiment("TestChannel", ["Airdrop confirmed!"])

        c = db_conn.cursor()
        c.execute("SELECT COUNT(*) FROM social_mentions WHERE app_name = 'TestChannel'")
        count = c.fetchone()[0]
        assert count >= 1

    def test_averages_multiple_texts(self, db_conn):
        from news_sentiment import analyze_channel_sentiment
        score = analyze_channel_sentiment("TestChannel", ["Airdrop!", "Scam alert!"])
        assert 0 <= score <= 100


class TestOpenAISentimentFallback:
    def test_falls_back_when_no_api_key(self, db_conn):
        from news_sentiment import _openai_sentiment
        with patch.dict("os.environ", {}, clear=True):
            score = _openai_sentiment(["Airdrop confirmed!"])
            assert score > 50

    def test_falls_back_on_api_error(self, db_conn):
        from news_sentiment import _openai_sentiment
        with patch.dict("os.environ", {"OPENAI_API_KEY": "fake-key"}):
            with patch("requests.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=500, text="Error")
                score = _openai_sentiment(["Test message"])
                assert 0 <= score <= 100


class TestHuggingFaceSentimentFallback:
    def test_falls_back_when_transformers_not_installed(self, db_conn):
        from news_sentiment import _huggingface_sentiment
        with patch.dict("sys.modules", {"transformers": None}):
            score = _huggingface_sentiment(["Airdrop confirmed!"])
            assert score > 50
