# Data Fetching SOP

## Goal
Fetch and normalize market events, holidays, and stock-specific info into a unified JSON schema.

## Data Sources
- **Akshare**: Used for A-shares (China) trading calendar.
- **YFinance**: Used for US stock market events (e.g., dividends, earnings for specific tickers).
- **Gov.cn**: Used for mainland China public holiday dates from the official State Council holiday notice page.
- **Hong Kong Government**: Used for Hong Kong public holiday dates and HK market-closure derivation.
- **OPM**: Used for US federal public holiday dates.
- **NYSE**: Used for US market-closure dates.
- **Federal Reserve**: Used for FOMC macro-event dates.

## Output Schema & Delivery
Data must adhere to the `Unified Event Schema` defined in `gemini.md`.
Instead of returning directly to the API router, data fetching tools should now write their results directly into the local SQLite database (`data/events.db`) using Upsert operations.

## Event Mapping
- `market_holiday`
  - CN market closures from `akshare`
  - HK market closures derived from Hong Kong Government holiday data
  - US market closures from NYSE holiday data
- `public_holiday`
  - CN public holidays from `gov.cn`
  - HK public holidays from Hong Kong Government
  - US public holidays from OPM
- `stock_event`
  - Earnings/dividend-related events from `yfinance`
- `macro_event`
  - FOMC meeting decision dates from the Federal Reserve calendar

## CN Public Holiday Notes
- The mainland China public holiday feed is parsed dynamically from the official `gov.cn` notice page.
- The fetcher expands the announced holiday ranges into one event per holiday date.
- No local JSON fixture is used for CN public holiday data.

## Error Handling
- If a data source fails or times out, catch the exception, log it, and return an empty list or cached data for that segment to ensure the main application does not crash.
- Ensure rate limits are respected (though less of an issue for akshare/yfinance locally).
- Do not fall back to hardcoded holiday JSON. If an upstream source is unavailable, return no events for that source and keep the cached DB snapshot intact.
- The fetch layer may return fewer events when an upstream source is unavailable, but it must not silently substitute static fixture data.
