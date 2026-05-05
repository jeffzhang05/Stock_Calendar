# Project Constitution

## 1. Project Map & State Tracking
- **North Star:** Build an automated, locally-executed script that fetches and aggregates market holidays (A-shares, HK, US), specific stock events, and macroeconomic events into a flexible, visualized calendar view.
- **Primary Data Source:** Dynamic upstream sources only. No holiday or event data should be hardcoded into local JSON fixtures.
- **Current CN Public Holiday Source:** Official China Government holiday notice page at `https://www.gov.cn/zhengce/zhengceku/202511/content_7047091.htm?sourcefrom=aladdin`.
- **Current Delivery Architecture:** Background refresh job writes to local SQLite; FastAPI serves only cached DB data.
- **Delivery Destination:** Web Application (FastAPI backend returning JSON + HTML/JS Frontend Visual Calendar).

## 2. Data Schemas
### Draft Unified Event Schema (JSON)
```json
{
  "events": [
    {
      "id": "string (unique identifier)",
      "date": "YYYY-MM-DD",
      "title": "string (e.g., 'Fed Rate Cut', 'US Market Closed')",
      "type": "enum: [market_holiday, public_holiday, stock_event, macro_event, custom]",
      "region": "enum: [CN, HK, US, GLOBAL]",
      "description": "string (optional details)",
      "related_tickers": ["string"]
    }
  ],
  "metadata": {
    "last_updated": "ISO8601 Timestamp",
    "version": "1.0"
  }
}
```

## 3. Behavioral Rules
- Retain flexibility for adding other event types easily.
- Execute locally via automated scripts (`start.sh`).
- UI must maintain a clean, professional aesthetic (Inter font, FullCalendar, distinct color tags for event types).
- Tickers of interest: NIO, NVDA, TSLA.
- Frontend navigation must not trigger live upstream API calls; it reads only cached event data from the backend.
- Year view should render as a 12-month overview with clickable mini-month cards that jump to the corresponding monthly view.
- Public holidays are a separate first-class event category in the UI and must not be grouped into market closures.

## 4. Architectural Invariants
- 3-Layer Architecture enforced: `architecture/` (SOPs), Navigation (LLM Routing), `tools/` (Python Scripts).
- No script writing until schema is approved.
- All temporary files reside in `.tmp/`.
- **Persistence Layer:** FastAPI must serve data exclusively from the local SQLite database (`data/events.db`). Background jobs handle the actual data fetching.
- **No Static Event Fixtures:** Holiday and event content must come from live upstream fetchers. Local files may store config, not business data snapshots.

## 4.1 Runtime Entry
- Frontend is not a separate dev server. `index.html` is served by `main.py`.
- Standard local start path:
  - `cd /Users/jeff/Desktop/Project/Stock_Calendar`
  - `./start.sh`
- Manual start path:
  - `cd /Users/jeff/Desktop/Project/Stock_Calendar`
  - `source venv/bin/activate`
  - `uvicorn main:app --port 8000`
- Local app URL: `http://127.0.0.1:8000`
- Background refresh command:
  - `cd /Users/jeff/Desktop/Project/Stock_Calendar`
  - `source venv/bin/activate`
  - `python tools/bg_refresh.py`
  - Default refresh window for date-bounded sources: previous year through next year
    - Example on 2026-05-05: `2025-01-01` to `2027-12-31`
- Web deployment path:
  - Python dependencies are defined in `requirements.txt`
  - Container runtime is defined in `Dockerfile`
  - Health endpoint: `GET /healthz`
  - SQLite path is configurable via `DB_PATH`
  - Fresh deployments can seed the DB on startup via `SEED_DB_IF_EMPTY=1`

## 5. Maintenance Log
- **2026-05-04:** Project initialized and completed.
  - Deployed FastAPI backend serving `akshare` (A-share holidays) and `yfinance` (US stock events for NIO, NVDA, TSLA).
  - Built responsive frontend using FullCalendar and Google Fonts.
  - Implemented `start.sh` for easy one-click local launching.
- **2026-05-04:** Backend contract aligned with current architecture.
  - Added `/api/events` filtering for `start_date`, `end_date`, `region`, and `type`.
  - Made tracked stock tickers configurable via `STOCK_CALENDAR_TICKERS`.
- **2026-05-05:** Added public holiday events for mainland China, Hong Kong, and the United States.
  - Added a dedicated `public_holiday` event stream backed by official 2026 holiday calendars.
  - Folded public holidays into the existing holiday filter group in the frontend.
- **2026-05-05:** Removed static holiday fixtures from the live path.
  - Mainland China public holidays are fetched dynamically from the official `gov.cn` holiday notice page.
  - Hong Kong public holidays are fetched dynamically from the Hong Kong Government page.
  - US public holidays are fetched dynamically from OPM.
  - HK and US market closures are fetched or derived dynamically from official sources.
  - Macro events are fetched dynamically from the Federal Reserve FOMC calendar.
- **2026-05-05:** Frontend year-view behavior changed from a long scrolling annual calendar to a 12-month overview.
  - `Year` now opens 12 mini-month cards for the selected year.
  - Clicking a mini-month jumps directly to that month's `dayGridMonth` view.
  - Year navigation buttons move between years without hitting live upstream APIs.
- **2026-05-05:** Public holidays were promoted to their own frontend event category.
  - `Public Holidays` now has its own dedicated filter tab.
  - `Market Closures` now controls only market-closure events.
- **2026-05-05:** Branch prepared for web deployment.
  - Added `requirements.txt` and `Dockerfile` for generic hosted runtime packaging.
  - Added `GET /healthz` for deployment checks.
  - Added configurable `DB_PATH`.
  - Added startup DB seeding support for fresh deployments.
