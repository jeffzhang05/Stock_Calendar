# Progress

## Initialization
- Project memory initialized (`task_plan.md`, `findings.md`, `progress.md`).
- Project constitution initialized (`gemini.md`).

## What was done
- Received partial Discovery answers regarding project goals and event types.
- Drafted initial JSON Data Schema in `gemini.md`.
- Completed Phase 2 (Link): Verified `akshare` and `yfinance` in `tools/test_data_sources.py`.
- Refactored `index.html` UI to use Inter font, modern cards, and loading states.
- Updated tracked tickers to NIO, NVDA, and TSLA.
- Created `start.sh` for one-click local deployment and background management.
- Aligned `/api/events` with documented filters for date range, region, and event type.
- Added a lightweight API filter smoke test in `tools/test_api_filters.py`.
- Removed visible sample macro records from the default dataset.
- Added HK/US market-closure generation for the visible calendar range.
- Added a year view plus clickable event-type filters in the frontend calendar UI.
- Reworked year view into a 12-month overview with clickable mini-month cards that jump to month view.
- Added public holiday event ingestion for China mainland, Hong Kong, and the United States.
- Split `public_holiday` into its own first-class frontend filter tab, separate from market closures.
- Migrated data serving to a local SQLite database (`data/events.db`) to eliminate live-fetching latency during navigation.
- Created `tools/bg_refresh.py` to upsert API data into the local database as a background/cron task.
- Refactored `/api/events` endpoint in `main.py` to read exclusively from the cached SQLite layer.
- Removed static holiday fixtures from the fetch path and replaced them with dynamic official-source fetchers for CN/HK/US holidays and HK/US market closures.
- Added dynamic macro events from the official Federal Reserve FOMC calendar.
- Confirmed mainland China public holidays now come from the official `gov.cn` holiday notice page, not from any local fixture.
- Added generic web deployment scaffolding: `requirements.txt`, `Dockerfile`, `/healthz`, configurable `DB_PATH`, and startup DB seeding.
- Added second-level frontend subtype filters so users can narrow visible events within a top-level category, including viewing only `CN ST` solar-term events.

## Errors & Fixes
- Addressed a minor urllib3 OpenSSL warning by acknowledging it doesn't break functionality.

## Tests & Results
- `tools/test_data_sources.py` executed successfully, retrieving A-share trade dates and AAPL info.
- Live endpoint verification succeeded for `/api/events`, including filtered requests such as `region=US&type=macro_event` and `start_date=2026-05-01&end_date=2026-05-31`.
- `tools/bg_refresh.py` completed successfully and populated `data/events.db` from dynamic upstream sources only.
- `tools/test_api_filters.py` passes against the DB-backed API path with dynamic public holiday and macro-event assertions.

## Next Todo
- Choose the actual public hosting target and wire deployment-specific config around the generic Docker/runtime path.
