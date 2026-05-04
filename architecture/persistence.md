# Persistence SOP

## Technology
SQLite3 (Built-in Python module). Database file stored at `data/events.db`.

## Goal
Decouple data ingestion (which can be slow and rate-limited) from data serving (which must be instantaneous).

## Schema
Table: `events`
- `id` (TEXT PRIMARY KEY) - Unique identifier for the event.
- `date` (TEXT) - Format YYYY-MM-DD.
- `title` (TEXT)
- `type` (TEXT) - e.g., 'market_holiday', 'public_holiday', 'stock_event', 'macro_event'.
- `region` (TEXT) - e.g., 'CN', 'US', 'HK'.
- `description` (TEXT)
- `related_tickers` (TEXT) - Comma-separated list or JSON array string.
- `last_updated` (TEXT) - ISO timestamp of when this record was last refreshed.

## Ingestion Rules
- Background jobs (e.g., `tools/bg_refresh.py`) are responsible for fetching from external APIs and using `INSERT OR REPLACE` (UPSERT) logic to update the `events` table.
- This ensures the database always has the freshest snapshot without duplicating data.
- The database is a cache only. Source-of-truth remains the live upstream providers.
- Static fixture files must not be used as event sources for refresh jobs.
