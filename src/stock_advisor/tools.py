import os
import json
import datetime as dt
import logging
from typing import List

import requests
import yfinance as yf
from transformers import pipeline
from langchain.agents import Tool

logger = logging.getLogger(__name__)

# Sentiment model is heavy; load once at module import
finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")


def sentiment_news(text: str):
    try:
        return json.dumps(finbert(text)[0])
    except Exception as exc:
        logger.error("FinBERT error: %s", exc)
        return "{}"


class _MarketNewsTool:
    name = "market_news"
    description = (
        "Fetch the latest 30 headlines for a ticker or topic. Returns JSON list "
        "with headline, summary, url, datetime."
    )

    def __call__(self, query: str):
        api_key = os.getenv("FINNHUB_KEY")
        if not api_key:
            return "FINNHUB_KEY not set"

        today = dt.date.today()
        frm = today - dt.timedelta(days=3)
        if query.isupper() and len(query) <= 5:
            url = (
                f"https://finnhub.io/api/v1/company-news?symbol={query}&from={frm}&to={today}&token={api_key}"
            )
        else:
            url = f"https://finnhub.io/api/v1/news?category=general&token={api_key}"

        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            articles = res.json()[:30]
        except Exception as exc:
            logger.error("Finnhub error: %s", exc)
            articles = []

        # Fallback to NewsAPI for breadth
        if len(articles) < 10 and os.getenv("NEWSAPI_KEY"):
            nurl = (
                "https://newsapi.org/v2/everything?q="
                f"{query}&language=en&sortBy=publishedAt&pageSize=30&apiKey={os.getenv('NEWSAPI_KEY')}"
            )
            try:
                na = requests.get(nurl, timeout=10).json().get("articles", [])
                for art in na:
                    articles.append(
                        {
                            "headline": art["title"],
                            "summary": art.get("description", ""),
                            "url": art["url"],
                            "datetime": art["publishedAt"],
                        }
                    )
            except Exception as exc:
                logger.error("NewsAPI error: %s", exc)
        if not articles:
            return "No recent news found."

        # Summarize as readable bullet list (max 5 headlines)
        summary_lines = []
        for article in articles[:5]:
            headline = article.get("headline") or article.get("title", "No headline")
            url = article.get("url", "")
            source = url.split('/')[2] if url else ""
            summary_lines.append(f"• {headline.strip()} ({source})")

        return "\n".join(summary_lines) + "\nEnd of news."



class StockQuoteTool:
    name = "stock_quote"
    description = "Return today's OHLC for a US ticker as JSON."

    def __call__(self, ticker: str):
        try:
            data = yf.Ticker(ticker).history(period="1d").iloc[-1]
            return json.dumps(
                {
                    "open": float(data.Open),
                    "high": float(data.High),
                    "low": float(data.Low),
                    "close": float(data.Close),
                }
            )
        except Exception as exc:
            logger.error("yfinance error: %s", exc)
            return "{}"


TOOLS: List[Tool] = [
    Tool(name=_MarketNewsTool.name, func=_MarketNewsTool(), description=_MarketNewsTool.description),
    Tool(name=StockQuoteTool.name, func=StockQuoteTool(), description=StockQuoteTool.description),
    Tool(name="news_sentiment", func=sentiment_news, description="Run FinBERT sentiment on text"),
]
