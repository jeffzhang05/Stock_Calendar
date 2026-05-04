import akshare as ak
from datetime import date, datetime, timedelta
import pandas as pd
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from tools.event_config import HK_PUBLIC_HOLIDAYS_URL, US_MARKET_HOLIDAYS_URL


def _resolve_window(start_date=None, end_date=None):
    today = datetime.now().date()
    resolved_start = start_date or date(today.year, 1, 1)
    resolved_end = end_date or date(today.year, 12, 31)
    return resolved_start, resolved_end


def _iter_weekdays(start_date, end_date):
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            yield current
        current += timedelta(days=1)


def _fetch_hk_market_closed_dates(year):
    response = requests.get(HK_PUBLIC_HOLIDAYS_URL, timeout=20)
    response.encoding = "utf-8"
    text = BeautifulSoup(response.text, "html.parser").get_text("\n")
    names = [
        "The first day of January",
        "Lunar New Year's Day",
        "The second day of Lunar New Year",
        "The third day of Lunar New Year",
        "Good Friday",
        "The day following Good Friday",
        "The day following Ching Ming Festival",
        "The day following Easter Monday",
        "Labour Day",
        "The day following the Birthday of the Buddha",
        "Tuen Ng Festival",
        "Hong Kong Special Administrative Region Establishment Day",
        "The day following the Chinese Mid-Autumn Festival",
        "National Day",
        "The day following Chung Yeung Festival",
        "Christmas Day",
        "The first weekday after Christmas Day",
    ]
    dates = set()
    for name in names:
        match = re.search(rf"{re.escape(name)}\s+([A-Za-z]+ \d{{1,2}})", text)
        if not match:
            continue
        holiday_date = datetime.strptime(f"{match.group(1)} {year}", "%B %d %Y").date()
        if holiday_date.weekday() < 5:
            dates.add(holiday_date)
    return dates


def _fetch_us_market_closed_dates(year):
    tables = pd.read_html(US_MARKET_HOLIDAYS_URL)
    target_table = None
    for table in tables:
        column_names = [str(col) for col in table.columns]
        if "2026" in column_names and "Holiday" in column_names:
            target_table = table
            break
    if target_table is None:
        raise RuntimeError("Could not locate the NYSE holiday table")

    dates = set()
    for _, row in target_table.iterrows():
        raw_value = str(row[str(year)] if str(year) in target_table.columns else row[year]).strip()
        if not raw_value or raw_value == "—*":
            continue
        raw_value = raw_value.split("(")[0].replace("*", "").strip()
        holiday_date = datetime.strptime(f"{raw_value}, {year}", "%A, %B %d, %Y").date()
        if holiday_date.weekday() < 5:
            dates.add(holiday_date)
    return dates


def _build_market_status_events(region, closed_dates, closed_title, market_name, start_date, end_date):
    events = []

    for day in _iter_weekdays(start_date, end_date):
        if day in closed_dates:
            events.append(
                {
                    "id": f"{region.lower()}_closed_{day.strftime('%Y%m%d')}",
                    "date": day.strftime("%Y-%m-%d"),
                    "title": closed_title,
                    "type": "market_holiday",
                    "region": region,
                    "description": f"{market_name} is closed.",
                }
            )
    return events


def fetch_market_holidays(start_date=None, end_date=None):
    """
    Fetches market status events.
    - CN closures come from Akshare's trading calendar.
    - US/HK open/closed weekdays come from local official schedule data.
    """
    events = []
    resolved_start, resolved_end = _resolve_window(start_date, end_date)
    try:
        # Get A-share trade calendar
        df = ak.tool_trade_date_hist_sina()
        df['trade_date'] = pd.to_datetime(df['trade_date'])

        all_dates = pd.date_range(start=resolved_start, end=resolved_end)
        trade_dates_set = set(df['trade_date'].dt.date)

        for d in all_dates:
            if d.weekday() < 5 and d.date() not in trade_dates_set:
                events.append({
                    "id": f"cn_holiday_{d.strftime('%Y%m%d')}",
                    "date": d.strftime("%Y-%m-%d"),
                    "title": "CN Closed",
                    "type": "market_holiday",
                    "region": "CN",
                    "description": "China A-Share market is closed."
                })
    except Exception as e:
        print(f"Error fetching holidays: {e}")

    years = range(resolved_start.year, resolved_end.year + 1)
    hk_closed_dates = set()
    us_closed_dates = set()
    for year in years:
        hk_closed_dates.update(_fetch_hk_market_closed_dates(year))
        us_closed_dates.update(_fetch_us_market_closed_dates(year))

    events.extend(
        _build_market_status_events(
            "HK",
            hk_closed_dates,
            "HK Closed",
            "HKEX Securities Market",
            resolved_start,
            resolved_end,
        )
    )
    events.extend(
        _build_market_status_events(
            "US",
            us_closed_dates,
            "US Closed",
            "NYSE",
            resolved_start,
            resolved_end,
        )
    )

    return events

if __name__ == "__main__":
    print(fetch_market_holidays())
