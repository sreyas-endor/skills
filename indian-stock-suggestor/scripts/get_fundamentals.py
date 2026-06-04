#!/usr/bin/env python3
"""Fetch live price + key fundamentals for NSE/BSE stocks via yfinance.

Usage:
    python3 get_fundamentals.py TICKER [TICKER ...]

TICKER is the NSE symbol (RELIANCE, INFY, HDFCBANK). ".NS" is appended
automatically; pass an explicit ".BO" suffix for BSE-only listings.

Outputs JSON to stdout. Notes for the analyst using this:
- yfinance does NOT provide ROCE, promoter holding, pledging, or Piotroski
  score — fetch those from Screener.in.
- ROE / margins / growth here are trailing-twelve-month figures.
- debt_to_equity is expressed as a percentage (e.g. 41.2 means 0.41x).
- Requires: pip install yfinance
"""

import json
import sys
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    sys.exit("yfinance not installed. Run: pip3 install yfinance")


def normalize(symbol: str) -> str:
    s = symbol.upper().strip()
    return s if s.endswith((".NS", ".BO")) else s + ".NS"


def fetch(symbol: str) -> dict:
    ticker = normalize(symbol)
    info = yf.Ticker(ticker).info or {}
    if not info.get("longName") and not info.get("regularMarketPrice"):
        return {"symbol": ticker, "error": "no data — check the ticker symbol"}
    return {
        "symbol": ticker,
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "currency": info.get("currency"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "market_cap": info.get("marketCap"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "pe_trailing": info.get("trailingPE"),
        "pe_forward": info.get("forwardPE"),
        "price_to_book": info.get("priceToBook"),
        "roe_ttm": info.get("returnOnEquity"),
        "net_profit_margin_ttm": info.get("profitMargins"),
        "operating_margin_ttm": info.get("operatingMargins"),
        "revenue_growth_yoy": info.get("revenueGrowth"),
        "earnings_growth_yoy": info.get("earningsGrowth"),
        "debt_to_equity_pct": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "free_cash_flow": info.get("freeCashflow"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "held_pct_insiders": info.get("heldPercentInsiders"),
        "held_pct_institutions": info.get("heldPercentInstitutions"),
        "analyst_rating": info.get("recommendationKey"),
        "analyst_count": info.get("numberOfAnalystOpinions"),
        "target_mean": info.get("targetMeanPrice"),
        "target_high": info.get("targetHighPrice"),
        "target_low": info.get("targetLowPrice"),
    }


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out = {
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "yfinance (Yahoo Finance)",
        "stocks": [fetch(s) for s in sys.argv[1:]],
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
