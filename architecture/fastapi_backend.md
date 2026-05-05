# Web Backend SOP

## Framework
FastAPI (Python)

## Goal
Serve the normalized event data to the frontend and host the static HTML/JS files.

## Endpoints
1. `GET /api/events`: Returns a JSON list of all events formatted according to the `Unified Event Schema`.
   - Optional query params: `start_date`, `end_date`, `region`, `type`.
   - `region` and `type` accept comma-separated values such as `CN,US` or `market_holiday,public_holiday,macro_event`.
   - Results should be date-sorted after filtering.
   - The frontend should pass the current calendar viewport range so the API returns only the visible month/week window.
2. `GET /`: Serves the main `index.html` visual calendar.
3. `GET /healthz`: Returns basic health and DB status for deployment checks.

## Architecture
- `main.py` in the root acts as the server.
- **Data Reads:** The API endpoints MUST strictly read from the local SQLite database (`data/events.db`).
- **No Live Fetching:** The backend router must NEVER call external APIs or blocking fetch functions directly. It serves only what is cached.
- Route-level logic is limited to lightweight filtering (by date/region/type) against the data returned from the SQLite database.
- Background refresh is delegated to `tools/bg_refresh.py`, which is the only supported ingestion path for live upstream event data.
- Default stock tickers are environment-configurable via `STOCK_CALENDAR_TICKERS`.
- On startup, the app initializes the DB and may seed it when empty.
