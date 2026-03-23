# How to Read Screener.in Data

Screener.in is the go-to free tool for Indian stock fundamental analysis. Here's how to use it effectively.

## URL structure
`https://www.screener.in/company/TICKER/` — replace TICKER with the NSE symbol (e.g., INFY, RELIANCE, HDFCBANK)

## Key sections on a Screener.in company page

### Top panel — Quick numbers
- **Market Cap**: Size of company (Large/Mid/Small cap context)
- **Current Price**: Live/delayed price
- **High/Low (52-week)**: Volatility context
- **P/E Ratio**: Price ÷ EPS. Compare with industry median P/E (shown on same page)
- **Book Value**: Net assets per share. P/B = Price ÷ Book Value
- **Dividend Yield**: Annual dividend ÷ price × 100
- **ROCE**: Return on Capital Employed — the most important single metric for quality businesses
- **ROE**: Return on Equity

### "About" section
Read this. It tells you what the company actually does, its business segments, and key subsidiaries.

### Quarterly Results table
- Look at last 4-8 quarters of Revenue and Net Profit
- Are they growing QoQ and YoY? Any sudden dips?
- Compare with analyst estimates if available

### Profit & Loss (Annual) — 10-year view
This is gold. Screener shows 10 years of:
- Sales (Revenue)
- Expenses
- Operating Profit (EBITDA)
- Net Profit
- EPS

Look for: consistent growth, no major loss years, expanding margins over time

### Balance Sheet — 10-year view
- **Borrowings**: Is debt growing faster than profits? Bad sign.
- **Reserves**: Growing reserves = retained earnings = wealth creation
- **Fixed Assets**: Capital-intensive or asset-light business?

### Cash Flow — 10-year view
**The most revealing section.**
- **Cash from Operations (CFO)**: Should be positive and close to net profit
- **Cash from Investing (CFI)**: Usually negative (investing in growth) — that's normal
- **Cash from Financing (CFF)**: Watch for frequent equity dilution (bad) or consistent buybacks (good)

**Key formula to compute**: CFO ÷ Net Profit × 100 = Cash Conversion %
- > 90% = excellent quality earnings
- 70-90% = acceptable
- < 70% = investigate why profits aren't converting to cash

### Ratios panel
- **Debtor Days**: How long customers take to pay. High = working capital stress.
- **Inventory Days**: How long goods sit unsold. High = demand issues.
- **Days Payable**: How long company takes to pay suppliers.
- **Cash Conversion Cycle** = Debtor Days + Inventory Days - Days Payable (lower is better)
- **ROCE, ROE over 10 years**: Track the trend. Declining ROCE = competitive pressure.

### Shareholding Pattern (quarterly)
- **Promoter %**: Should be stable or increasing. Sudden drop = concern.
- **Pledged %**: Any pledging is a yellow flag; > 20% is a red flag.
- **FII %**: Rising FII = institutional confidence. Check the trend.
- **DII %**: Domestic mutual funds and insurance companies.
- **Public %**: Retail investors.

### Peers comparison table
Screener shows sector peers with key ratios. Always compare:
- Is this company's P/E higher or lower than peers? Is the premium justified?
- Is ROCE/ROE better than peers?
- Is growth faster than peers?

## Screener.in screens (stock filters)

You can create custom filters at `https://www.screener.in/explore/`

Useful filter for long-term quality stocks:
```
Return on capital employed > 15 AND
Debt to equity < 0.5 AND
Sales growth 5Years > 15 AND
Profit growth 5Years > 15 AND
Promoter holding > 35 AND
Market Capitalization > 500
```

Popular curated screens to explore:
- "Magic Formula" stocks
- "Coffee Can" style screens (high ROCE + high growth for 10 years)
- Ben Graham-style deep value screens

## Limitations of Screener.in
- Data is updated with a lag (usually 24-48 hours after BSE/NSE filings)
- Doesn't have analyst price targets or ratings — use Trendlyne/Moneycontrol for that
- Consolidated vs Standalone: Always look at **Consolidated** financials if available (includes subsidiaries)
