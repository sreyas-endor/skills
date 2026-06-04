# Analyzing Earnings Concalls for Indian Stocks

Concall (earnings call) transcripts are the highest-signal source for judging management quality and forward outlook — numbers tell you what happened, concalls tell you what management *thinks* will happen and whether they can be trusted.

## Where to find transcripts (in fallback order)

1. **Screener.in** — company page → "Documents" section → "Concalls" tab. Links transcripts, PPTs, and audio recordings per quarter. Fastest route.
2. **BSE filings** — `https://www.bseindia.com/` → company → Announcements. Transcripts are mandatory filings (usually within 5 working days of the call).
3. **Company IR page** — investor relations section; also has the earnings presentation.
4. **Search fallback** — `"[company] Q[n] FY[yy] earnings call transcript"`.

Earnings presentations (PPTs) are a faster skim than full transcripts — start there, go to the transcript for management Q&A.

## What to extract

### From the management commentary
- **Guidance**: revenue/margin/capex guidance for the next year. Write down the numbers — you'll compare them against delivery next quarter.
- **Growth triggers**: new capacity coming online, new client wins, new product launches, China+1 orders, regulatory tailwinds. Rank each by probability and impact.
- **Margin walk**: why margins moved — raw material, mix, pricing, one-offs? "One-off" appearing every quarter is a red flag.
- **Capex plans**: expansion signals confidence; check how it's funded (internal accruals = good, repeated equity raises = caution).

### From the analyst Q&A (the most honest section)
- Which questions did management **answer directly with numbers** vs deflect?
- Repeated analyst pushback on the same topic across quarters = the street doesn't believe management on that point.
- New analysts appearing from larger houses = growing institutional interest.

### Track record check (do this across 4+ quarters)
The single best management-quality test: **guidance vs delivery**.
- Pull guidance from concalls 2-4 quarters ago and compare with reported numbers.
- Consistently delivering or beating = credible management; chronic overpromising = discount everything they say.

## Red flags specific to concalls

- Guidance cut blamed entirely on external factors, every time
- Evasive or hostile answers to working-capital / receivables / pledging questions
- CFO absent from the call without explanation, or a new CFO every couple of years
- Aggressive non-GAAP framing ("adjusted EBITDA" doing heavy lifting)
- Big gap between the upbeat narrative and flat/declining numbers

## Output format for concall analysis

```
## [Company] Q[n] FY[yy] Concall — Key Takeaways

### Quarter in one line
### Guidance given (with numbers, vs last guidance)
### Growth triggers (ranked by probability × impact)
### Management credibility check (guidance vs delivery, last 4 quarters)
### Q&A signals (what analysts pushed on; what was dodged)
### Red flags / watch items
### What this changes for the investment thesis
```

Cite the transcript (quarter, date, source link) for every claim, per the data-discipline rules in SKILL.md.
