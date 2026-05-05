from datetime import date
from typing import List, Optional, Set

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

from tools.bg_refresh import run_refresh
from tools.db import get_event_count, get_events as db_get_events, init_db

app = FastAPI(title="Stock Calendar API")

class Event(BaseModel):
    id: str
    date: str
    title: str
    type: str
    region: str
    description: Optional[str] = ""
    related_tickers: Optional[List[str]] = []


def _parse_csv_filter(raw_value: Optional[str], *, normalizer=str.upper) -> Optional[List[str]]:
    if not raw_value:
        return None
    # We use List instead of Set so we can pass it easily to sqlite IN clause placeholders
    values = list({normalizer(part.strip()) for part in raw_value.split(",") if part.strip()})
    return values or None


@app.on_event("startup")
def startup():
    init_db()
    auto_refresh = os.getenv("AUTO_REFRESH_ON_STARTUP", "0") == "1"
    seed_if_empty = os.getenv("SEED_DB_IF_EMPTY", "1") == "1"

    event_count = get_event_count()
    if auto_refresh or (seed_if_empty and event_count == 0):
        run_refresh()


@app.get("/api/events", response_model=List[Event])
def get_events(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    region: Optional[str] = Query(default=None, description="Comma-separated region codes, e.g. CN,US"),
    event_type: Optional[str] = Query(
        default=None,
        alias="type",
        description="Comma-separated event types, e.g. market_holiday,stock_event",
    ),
):
    regions = _parse_csv_filter(region, normalizer=str.upper)
    event_types = _parse_csv_filter(event_type, normalizer=str.lower)

    # Note: SQLite date comparisons work string-wise with YYYY-MM-DD
    str_start = start_date.isoformat() if start_date else None
    str_end = end_date.isoformat() if end_date else None

    # Fetch directly from the SQLite database
    filtered_events = db_get_events(
        start_date=str_start, 
        end_date=str_end, 
        regions=regions, 
        types=event_types
    )
    
    return filtered_events


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "event_count": get_event_count(),
        "db_path": os.getenv("DB_PATH", "data/events.db"),
    }

@app.get("/")
def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Index.html not found. Please create it.</h1>", status_code=404)
