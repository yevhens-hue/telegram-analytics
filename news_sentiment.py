import os
import logging
from datetime import datetime
from typing import Optional, List
from db_utils import save_social_mention

logger = logging.getLogger(__name__)

BULLISH_KEYWORDS = ["airdrop", "listing", "partnership", "growth", "buy", "pump", "alpha", "moon", "bullish", "gem"]
BEARISH_KEYWORDS = ["scam", "delay", "hack", "dump", "sell", "rug", "exploit", "bearish", "rekt", "fud"]

SENTIMENT_BACKEND = os.environ.get("SENTIMENT_BACKEND", "keyword")  # keyword | huggingface | openai


def _keyword_sentiment(text: str) -> float:
    """Rule-based sentiment score from keywords."""
    text_lower = text.lower()
    score = 50.0
    for kw in BULLISH_KEYWORDS:
        if kw in text_lower:
            score += 5
    for kw in BEARISH_KEYWORDS:
        if kw in text_lower:
            score -= 10
    return min(100.0, max(0.0, score))


def _huggingface_sentiment(texts: List[str]) -> float:
    """Sentiment analysis via HuggingFace transformers pipeline."""
    try:
        from transformers import pipeline as hf_pipeline
    except ImportError:
        logger.warning("transformers не установлен. Установите: pip install transformers torch. Fallback на keyword.")
        return _keyword_sentiment(" ".join(texts))

    try:
        classifier = hf_pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            top_k=None,
            truncation=True,
            max_length=512,
        )
        total_score = 0.0
        count = 0
        for text in texts[:10]:
            results = classifier(text[:512])
            if results and isinstance(results[0], list):
                label_scores = {r["label"].lower(): r["score"] for r in results[0]}
                pos = label_scores.get("positive", 0)
                neg = label_scores.get("negative", 0)
                total_score += 50 + (pos - neg) * 50
                count += 1
        return min(100.0, max(0.0, total_score / max(1, count)))
    except Exception as e:
        logger.error("HuggingFace sentiment error: %s. Fallback на keyword.", e)
        return _keyword_sentiment(" ".join(texts))


def _openai_sentiment(texts: List[str]) -> float:
    """Sentiment analysis via OpenAI API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY не задан. Fallback на keyword.")
        return _keyword_sentiment(" ".join(texts))

    try:
        import requests
        combined = "\n".join(texts[:10])
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": "You are a crypto market sentiment analyzer. Given Telegram messages, respond with ONLY a single number from 0 (extreme bearish) to 100 (extreme bullish). No explanation."},
                    {"role": "user", "content": f"Analyze the sentiment of these Telegram messages:\n{combined}"},
                ],
                "max_tokens": 10,
                "temperature": 0,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            score_str = resp.json()["choices"][0]["message"]["content"].strip()
            score = float(score_str)
            return min(100.0, max(0.0, score))
        else:
            logger.error("OpenAI API error %d: %s", resp.status_code, resp.text[:200])
            return _keyword_sentiment(" ".join(texts))
    except Exception as e:
        logger.error("OpenAI sentiment error: %s. Fallback на keyword.", e)
        return _keyword_sentiment(" ".join(texts))


def analyze_channel_sentiment(channel_name: str, texts: Optional[List[str]] = None) -> float:
    """
    Analyze sentiment for a channel. Supports three backends:
    - keyword: rule-based (default)
    - huggingface: local HuggingFace transformers
    - openai: OpenAI API
    """
    logger.info("Анализ сентимента для %s (backend: %s)...", channel_name, SENTIMENT_BACKEND)

    if SENTIMENT_BACKEND == "huggingface" and texts:
        score = _huggingface_sentiment(texts)
    elif SENTIMENT_BACKEND == "openai" and texts:
        score = _openai_sentiment(texts)
    elif texts:
        scores = [_keyword_sentiment(t) for t in texts]
        score = sum(scores) / len(scores) if scores else 50.0
    else:
        score = 50.0

    final_score = min(100.0, max(0.0, score))
    logger.info("  -> Sentiment Score: %.0f/100 (%s)", final_score, SENTIMENT_BACKEND)

    if texts:
        today = datetime.now().strftime("%Y-%m-%d")
        save_social_mention(channel_name, "telegram", " ".join(texts[:3])[:500], final_score, today)

    return final_score


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = analyze_channel_sentiment("Hamster Kombat", ["Airdrop is coming! Bullish on TON!", "Great partnership announced"])
    print(f"Sentiment: {result}")
