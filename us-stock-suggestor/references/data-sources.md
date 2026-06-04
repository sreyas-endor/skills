# US Stock Data Sources — Verified Access Guide

All sources below were verified by actual fetches (June 2026). Re-verify if a fetch starts failing — anti-bot policies change.

## Tier 1: Primary sources (plain WebFetch works)

### StockAnalysis.com — the Screener.in of US markets
The single best free source. All pages fetchable without login.

| Page | URL pattern | Key data |
|------|-------------|----------|
| Overview | `https://stockanalysis.com/stocks/TICKER/` | Price, market cap, analyst target + consensus, shares outstanding |
| Income statement | `https://stockanalysis.com/stocks/TICKER/financials/` | TTM + ~10 fiscal years: revenue, net income, op income, gross profit, diluted EPS, all margins, YoY growth, EBITDA, FCF/share |
| Balance sheet | `.../financials/balance-sheet/` | Cash, debt, equity, working capital history |
| Cash flow | `.../financials/cash-flow-statement/` | OCF, capex, FCF, SBC, buybacks, dividends history |
| Ratios | `.../financials/ratios/` | Historical P/E, ROE, ROIC, debt ratios by year |
| Statistics | `https://stockanalysis.com/stocks/TICKER/statistics/` | P/E, fwd P/E, P/B, P/S, PEG, ROE, **ROIC**, ROA, ROCE, margins, Debt/Equity, Debt/EBITDA, Current Ratio, div yield, EV, EV/EBITDA, short interest |
| Forecast | `https://stockanalysis.com/stocks/TICKER/forecast/` | Avg/high/low price target, consensus rating, analyst count, FY revenue & EPS forecasts |

Free tier caps history at ~10 years (plenty). For ETFs: `https://stockanalysis.com/etf/TICKER/`.

### Finviz — one-page snapshot + ownership
- `https://finviz.com/quote.ashx?t=TICKER`
- Everything on one page: P/E, Fwd P/E, PEG, P/S, P/B, P/C, P/FCF, ROE, ROA, ROIC, gross/op/net margins, Debt/Eq, LT Debt/Eq, Current/Quick ratio, EPS growth (this yr/next yr/next 5Y/past 5Y), sales growth, **Insider Own %, Insider Trans %, Inst Own %, Inst Trans %**, short float, analyst recom (1=Strong Buy → 5=Sell), target price, 52W range, beta, ATR
- Screener for idea generation: `https://finviz.com/screener.ashx?v=111&f=...` (filter params: `fa_roe_o15` ROE>15%, `fa_debteq_u0.5` D/E<0.5, `cap_midover` mid+ cap, etc.)
- Note: standalone insider page renders empty in plain fetch — use the per-quote page

### MarketBeat — analyst consensus
- `https://www.marketbeat.com/stocks/NASDAQ/TICKER/price-target/` (use `/stocks/NYSE/TICKER/` for NYSE listings)
- Consensus rating, avg target, analyst count, high/low targets, upside %, buy/hold/sell breakdown

### Benzinga — per-firm analyst table
- `https://www.benzinga.com/quote/TICKER/analyst-ratings`
- Consensus + table of individual firm ratings with dates (good for spotting recent upgrade/downgrade clusters)

### Dataroma — superinvestor 13F holdings
- `https://dataroma.com/m/stock.php?sym=TICKER`
- Which famous value funds (Buffett, Ackman, Li Lu, etc.) hold the stock, % of their portfolio, recent adds/trims, insider buy/sell summary
- Grand portfolio view: `https://dataroma.com/m/home.php`

### Simply Wall St — scorecard (Tickertape equivalent)
- URL has a sector slug; search `"site:simplywall.st [company name]"` to find the exact page
- "Snowflake" scores: Valuation, Future Growth, Past Performance, Financial Health, Dividends (each /6); P/E vs industry, fair-value estimate

## Tier 2: SEC EDGAR (use Bash/curl — WebFetch gets 403)

SEC requires a `User-Agent: name email` header. Works perfectly via curl:

```bash
UA="User-Agent: research ss@endor.ai"

# 1. Resolve ticker → CIK (zero-pad CIK to 10 digits)
curl -s -H "$UA" https://www.sec.gov/files/company_tickers.json | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(next(f\"{v['cik_str']:010d}\" for v in d.values() if v['ticker']=='AAPL'))"

# 2. All XBRL facts (every audited number, 10yr+) — large file (~3-4MB)
curl -s -H "$UA" https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json

# 3. Single concept (targeted, small)
curl -s -H "$UA" https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/NetIncomeLoss.json

# 4. Filing history (10-K, 10-Q, 8-K, Form 4 insider trades)
curl -s -H "$UA" https://data.sec.gov/submissions/CIK0000320193.json
```

Useful us-gaap tags: `RevenueFromContractWithCustomerExcludingAssessedTax` (or `Revenues`), `NetIncomeLoss`, `OperatingIncomeLoss`, `NetCashProvidedByUsedInOperatingActivities`, `PaymentsToAcquirePropertyPlantAndEquipment` (capex), `ShareBasedCompensation`, `CommonStockSharesOutstanding`, `Assets`, `Liabilities`, `StockholdersEquity`, `LongTermDebt`.

EDGAR is the gold standard for: audited 10yr+ history, exact SBC numbers, share count trends, Form 4 insider transactions. Use it when StockAnalysis numbers need verification or deeper history.

## Tier 3: Price only

- Yahoo chart API (JSON, no key): `https://query1.finance.yahoo.com/v8/finance/chart/TICKER`
  - Returns: regularMarketPrice, 52-wk range, OHLCV arrays. Price data ONLY — quoteSummary/v7 endpoints are dead (need crumb+cookie).

## ❌ Blocked — do not waste fetches on these

| Source | Status |
|--------|--------|
| macrotrends.net | HTTP 402 anti-bot |
| zacks.com | Cloudflare challenge |
| gurufocus.com | 403 |
| tipranks.com | 403 |
| whalewisdom.com | Data paywalled |
| wsj.com/market-data | Fetch refused |
| finance.yahoo.com HTML pages | 503 / JS-rendered |
| Yahoo quoteSummary API | 401 (crumb+cookie required) |

If you need data only these have, fall back to WebSearch and read the search snippets/cached results instead.

## Recommended fetch sequence for a full analysis

1. `stockanalysis.com/stocks/T/statistics/` — valuation + quality ratios (one fetch, most metrics)
2. `stockanalysis.com/stocks/T/financials/` — growth history
3. `stockanalysis.com/stocks/T/forecast/` — analyst consensus
4. `finviz.com/quote.ashx?t=T` — ownership % + cross-check
5. `dataroma.com/m/stock.php?sym=T` — smart money (optional)
6. SEC EDGAR via curl — only when verifying SBC, share count, or filing details
7. WebSearch for recent news/earnings: `"[Company] Q[N] [year] earnings results"`

Steps 1-4 are independent — fetch them in parallel.
