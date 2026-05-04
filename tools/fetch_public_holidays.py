from datetime import date, datetime, timedelta
import re
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup

from tools.event_config import CN_PUBLIC_HOLIDAYS_URL, HK_PUBLIC_HOLIDAYS_URL, US_PUBLIC_HOLIDAYS_URL


def _resolve_window(start_date=None, end_date=None):
    today = datetime.now().date()
    resolved_start = start_date or date(today.year, 1, 1)
    resolved_end = end_date or date(today.year, 12, 31)
    return resolved_start, resolved_end


def _expand_date_range(year, start_month, start_day, end_month, end_day):
    current = date(year, start_month, start_day)
    end = date(year, end_month, end_day)
    items = []
    while current <= end:
        items.append(current)
        current += timedelta(days=1)
    return items


def _fetch_cn_public_holidays(year):
    response = requests.get(CN_PUBLIC_HOLIDAYS_URL, timeout=20)
    response.encoding = "utf-8"
    text = BeautifulSoup(response.text, "html.parser").get_text("\n")
    patterns = [
        ("元旦", "New Year's Day", r"一、元旦：\s*(\d+)月(\d+)日.*?至(\d+)日"),
        ("春节", "Spring Festival", r"二、春节：\s*(\d+)月(\d+)日.*?至(\d+)日"),
        ("清明节", "Qingming Festival", r"三、清明节：\s*(\d+)月(\d+)日.*?至(\d+)日"),
        ("劳动节", "Labour Day", r"四、劳动节：\s*(\d+)月(\d+)日.*?至(\d+)日"),
        ("端午节", "Dragon Boat Festival", r"五、端午节：\s*(\d+)月(\d+)日.*?至(\d+)日"),
        ("中秋节", "Mid-Autumn Festival", r"六、中秋节：\s*(\d+)月(\d+)日.*?至(\d+)日"),
        ("国庆节", "National Day", r"七、国庆节：\s*(\d+)月(\d+)日.*?至(\d+)日"),
    ]

    events = []
    for label_cn, label_en, pattern in patterns:
        match = re.search(pattern, text, re.S)
        if not match:
            continue
        start_month, start_day, end_day = map(int, match.groups())
        for holiday_date in _expand_date_range(year, start_month, start_day, start_month if label_cn != "国庆节" else 10, end_day):
            events.append(
                {
                    "id": f"cn_public_{holiday_date.strftime('%Y%m%d')}",
                    "date": holiday_date.isoformat(),
                    "region": "CN",
                    "title": f"CN Public Holiday: {label_en}",
                    "description": f"Public holiday in mainland China for {label_en}.",
                }
            )
    return events


def _fetch_hk_public_holidays(year):
    response = requests.get(HK_PUBLIC_HOLIDAYS_URL, timeout=20)
    response.encoding = "utf-8"
    text = BeautifulSoup(response.text, "html.parser").get_text("\n")
    patterns = [
        ("The first day of January", "New Year's Day"),
        ("Lunar New Year's Day", "Lunar New Year's Day"),
        ("The second day of Lunar New Year", "Second Day of Lunar New Year"),
        ("The third day of Lunar New Year", "Third Day of Lunar New Year"),
        ("Good Friday", "Good Friday"),
        ("The day following Good Friday", "Day Following Good Friday"),
        ("The day following Ching Ming Festival", "Day Following Ching Ming Festival"),
        ("The day following Easter Monday", "Day Following Easter Monday"),
        ("Labour Day", "Labour Day"),
        ("The day following the Birthday of the Buddha", "Day Following Birthday of the Buddha"),
        ("Tuen Ng Festival", "Tuen Ng Festival"),
        ("Hong Kong Special Administrative Region Establishment Day", "HKSAR Establishment Day"),
        ("The day following the Chinese Mid-Autumn Festival", "Day Following the Chinese Mid-Autumn Festival"),
        ("National Day", "National Day"),
        ("The day following Chung Yeung Festival", "Day Following Chung Yeung Festival"),
        ("Christmas Day", "Christmas Day"),
        ("The first weekday after Christmas Day", "First Weekday After Christmas Day"),
    ]

    events = []
    for source_name, title_name in patterns:
        match = re.search(rf"{re.escape(source_name)}\s+([A-Za-z]+ \d{{1,2}})", text)
        if not match:
            continue
        holiday_date = datetime.strptime(f"{match.group(1)} {year}", "%B %d %Y").date()
        events.append(
            {
                "id": f"hk_public_{holiday_date.strftime('%Y%m%d')}",
                "date": holiday_date.isoformat(),
                "region": "HK",
                "title": f"HK Public Holiday: {title_name}",
                "description": "General holiday in Hong Kong.",
            }
        )
    return events


def _fetch_us_public_holidays(year):
    tables = pd.read_html(US_PUBLIC_HOLIDAYS_URL)
    target_table = None
    for table in tables:
        column_names = [str(col) for col in table.columns]
        if column_names != ["Date", "Holiday"]:
            continue
        rendered = table.astype(str).to_string()
        if "Friday, June 19" in rendered and "Friday, July 03" in rendered:
            target_table = table
            break
    if target_table is None:
        raise RuntimeError("Could not locate the 2026 OPM federal holiday table")

    events = []
    for _, row in target_table.iterrows():
        raw_date = str(row["Date"]).replace("*", "").strip()
        holiday_date = datetime.strptime(f"{raw_date}, {year}", "%A, %B %d, %Y").date()
        holiday_name = str(row["Holiday"]).strip()
        events.append(
            {
                "id": f"us_public_{holiday_date.strftime('%Y%m%d')}",
                "date": holiday_date.isoformat(),
                "region": "US",
                "title": f"US Public Holiday: {holiday_name}",
                "description": "Federal holiday in the United States.",
            }
        )
    return events


def fetch_public_holidays(start_date=None, end_date=None) -> List[dict]:
    resolved_start, resolved_end = _resolve_window(start_date, end_date)
    years = range(resolved_start.year, resolved_end.year + 1)
    events = []
    for year in years:
        events.extend(_fetch_cn_public_holidays(year))
        events.extend(_fetch_hk_public_holidays(year))
        events.extend(_fetch_us_public_holidays(year))

    filtered_events = []
    for event in events:
        event_date = date.fromisoformat(event["date"])
        if resolved_start <= event_date <= resolved_end:
            filtered_events.append(
                {
                    "id": event["id"],
                    "date": event["date"],
                    "title": event["title"],
                    "type": "public_holiday",
                    "region": event["region"],
                    "description": event.get("description", ""),
                    "related_tickers": [],
                }
            )
    return filtered_events


if __name__ == "__main__":
    print(fetch_public_holidays())
