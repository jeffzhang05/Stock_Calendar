from datetime import date, datetime
import re
from typing import List

import requests
from bs4 import BeautifulSoup

FOMC_CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def _resolve_window(start_date=None, end_date=None):
    today = datetime.now().date()
    resolved_start = start_date or date(today.year, 1, 1)
    resolved_end = end_date or date(today.year, 12, 31)
    return resolved_start, resolved_end


def _extract_year_section(full_text, year):
    matches = list(re.finditer(r"(\d{4}) FOMC Meetings", full_text))
    positions = [(int(match.group(1)), match.start(), match.end()) for match in matches]
    for index, (matched_year, _, end_pos) in enumerate(positions):
        if matched_year != year:
            continue
        next_start = positions[index + 1][1] if index + 1 < len(positions) else len(full_text)
        return full_text[end_pos:next_start]
    return ""


def fetch_macro_events(start_date=None, end_date=None) -> List[dict]:
    resolved_start, resolved_end = _resolve_window(start_date, end_date)

    response = requests.get(FOMC_CALENDAR_URL, timeout=20)
    response.encoding = "utf-8"
    text = BeautifulSoup(response.text, "html.parser").get_text("\n")

    events = []
    for year in range(resolved_start.year, resolved_end.year + 1):
        section = _extract_year_section(text, year)
        if not section:
            continue

        for month_name, start_day, end_day, has_sep in re.findall(r"([A-Z][a-z]+)\s+(\d{1,2})-(\d{1,2})(\*)?", section):
            month_number = MONTHS.get(month_name)
            if not month_number:
                continue

            decision_date = date(year, month_number, int(end_day))
            if decision_date < resolved_start or decision_date > resolved_end:
                continue

            description = "Federal Reserve FOMC meeting concludes with a policy decision."
            if has_sep:
                description += " This meeting is associated with a Summary of Economic Projections."

            events.append(
                {
                    "id": f"macro_fomc_{decision_date.strftime('%Y%m%d')}",
                    "date": decision_date.isoformat(),
                    "title": "FOMC Rate Decision",
                    "type": "macro_event",
                    "region": "US",
                    "description": description,
                    "related_tickers": [],
                }
            )

    return events


if __name__ == "__main__":
    print(fetch_macro_events())
