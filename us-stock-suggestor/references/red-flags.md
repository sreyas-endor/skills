# US Stock Red Flags — Quality & Governance Issues

US markets have stronger regulation than India (less promoter-style fraud) but their own distinct traps. This guide covers what to watch for.

## 🚨 High-severity red flags (avoid or demand answers)

### Stock-based compensation (SBC) dilution treadmill
The #1 US-specific trap, especially in tech. Companies report "adjusted" profitability while paying employees in stock, diluting shareholders 3-8% per year.
- **How to check**: Cash flow statement (StockAnalysis `/cash-flow-statement/`) — SBC line; compare to revenue and FCF
- **Thresholds**: SBC/Revenue > 10% is concerning; > 15-20% means shareholders fund payroll. Also check share count: if diluted shares grow > 3%/yr despite "buybacks", the buybacks just mop up SBC
- **The tell**: company touts "FCF" but FCF − SBC is negative

### Non-GAAP earnings games
"Adjusted EBITDA" that excludes SBC, restructuring (every year), amortization, and litigation. If adjusted earnings are consistently 2x+ GAAP earnings, management is hiding real costs.
- **How to check**: compare GAAP EPS vs adjusted EPS in the earnings release; read the reconciliation table
- **WeWork's "Community Adjusted EBITDA"** is the canonical cautionary tale

### Going-concern / cash runway (unprofitable companies)
- **How to check**: cash + short-term investments vs annual FCF burn. Runway < 18 months means a dilutive raise is coming
- 10-K "going concern" language is an automatic avoid for a long-term portfolio

### Serial acquirers with ballooning goodwill
Roll-ups that grow only via acquisition, funded by debt/stock. Goodwill > 50% of total assets + rising debt = future impairment risk.
- **How to check**: balance sheet goodwill trend; "organic growth" disclosure (or its absence)

### Channel stuffing / receivables outrunning revenue
Accounts receivable or inventory growing much faster than revenue for 2+ quarters = demand being pulled forward or fabricated.
- **How to check**: balance sheet AR/inventory growth vs revenue growth; DSO trend

### Short-seller reports with specifics
A Hindenburg/Muddy Waters-style report alleging specific accounting fraud (not just "overvalued") deserves a real read before buying. Search: `"[Company] short seller report"`.

## ⚠️ Medium-severity red flags (investigate before buying)

### Insider selling clusters
Routine 10b5-1 plan sales are noise. **Clusters** of open-market sales by CEO+CFO+directors within weeks, outside scheduled plans, especially after a run-up — pay attention.
- **How to check**: Finviz quote page insider table; SEC Form 4 filings via EDGAR

### Executive churn
CFO resignations "to pursue other opportunities" with < 2 years tenure, especially if followed by auditor change or restatement. Two CFOs in 3 years = something's wrong in the numbers.

### Auditor issues
- Restatements of prior financials
- Material weakness in internal controls (disclosed in 10-K Item 9A)
- Auditor resignation (8-K filing) — rarer and more serious in the US than India

### Customer concentration
One customer > 20% of revenue (disclosed in 10-K). Common in semis/defense suppliers — not fatal, but price the risk.

### Heavy debt + cyclical business
Net debt/EBITDA > 3x in a cyclical (autos, airlines, commodities) means equity can get wiped in a downturn. Fine in stable cash flows (utilities, towers), dangerous in cyclicals.

### Dual-class shares with tiny founder economic stake
Founder controls 90% of votes with 5% of economics and a history of ignoring shareholders. Not automatically bad (GOOGL, META worked out) — but check the founder's track record.

## 🟡 Situational / hype red flags

### Meme-stock dynamics
Short float > 20% + retail-forum frenzy + price disconnected from fundamentals = trading vehicle, not an investment. Fine to acknowledge; not for the long-term portfolio.

### Recent SPAC / recent IPO lockup
- De-SPAC companies have a brutal base rate (most are down 70%+ from merger). Demand 2+ years of delivered (not projected) numbers
- IPO lockup expiry (~180 days post-IPO) often brings insider supply — check the date before buying a recent IPO

### Story-stock projections
"TAM is $1 trillion" + hockey-stick revenue projections + no current revenue. Pre-revenue companies are venture bets, size accordingly (or avoid).

### Dividend trap
Yield > 7% usually means the market expects a cut. Check payout ratio (dividends/FCF > 80% = unsustainable) before recommending any high-yielder.

## Quick checklist to run on every stock

```
□ SBC/Revenue < 10%? Share count flat or shrinking?
□ GAAP vs non-GAAP gap reasonable?
□ FCF positive (or clear path + 18mo runway)?
□ AR/inventory growing in line with revenue?
□ No CFO/auditor churn in last 3 years?
□ No material weakness / restatement?
□ Insider buys > sells (or at least no panic clusters)?
□ Net debt/EBITDA < 3x (or appropriate for sector)?
□ No credible short report outstanding?
□ Not a recent de-SPAC / pre-lockup IPO?
```

7+ clean = governance pass. Any high-severity flag = explain it prominently in the analysis.
