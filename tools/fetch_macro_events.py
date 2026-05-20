from datetime import date, datetime, timedelta
import re
from typing import List
import calendar

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

# Official/Revised BLS Release Dates for 2026
# These are the dates the reports are RELEASED to the public.
BLS_2026_SCHEDULE = {
    "NFP": [
        "2026-01-09", "2026-02-11", "2026-03-06", "2026-04-03", 
        "2026-05-08", "2026-06-05", "2026-07-02", "2026-08-07", 
        "2026-09-04", "2026-10-02", "2026-11-06", "2026-12-04"
    ],
    "CPI": [
        "2026-01-13", "2026-02-13", "2026-03-11", "2026-04-10", 
        "2026-05-12", "2026-06-10", "2026-07-14", "2026-08-12", 
        "2026-09-11", "2026-10-14", "2026-11-10", "2026-12-10"
    ],
    "PPI": [
        "2026-01-30", "2026-02-27", "2026-03-18", "2026-04-14", 
        "2026-05-13", "2026-06-11", "2026-07-15", "2026-08-13", 
        "2026-09-15", "2026-10-15", "2026-11-13", "2026-12-11"
    ]
}


def _resolve_window(start_date=None, end_date=None):
    today = datetime.now().date()
    resolved_start = start_date or date(today.year, 1, 1)
    resolved_end = end_date or date(today.year, 12, 31)
    return resolved_start, resolved_end


def _get_nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Finds the nth instance of a weekday in a given month. weekday: 0-Mon, 4-Fri."""
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    month_days = cal.monthdatescalendar(year, month)
    count = 0
    for week in month_days:
        for day in week:
            if day.weekday() == weekday and day.month == month:
                count += 1
                if count == n:
                    return day
    return None


def _get_last_weekday(year: int, month: int, weekday: int) -> date:
    """Finds the last instance of a weekday in a given month."""
    last_day = calendar.monthrange(year, month)[1]
    d = date(year, month, last_day)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def _derive_options_expirations(start_date: date, end_date: date) -> List[dict]:
    events = []
    current = start_date.replace(day=1)
    while current <= end_date:
        exp_date = _get_nth_weekday(current.year, current.month, 4, 3)
        if exp_date and start_date <= exp_date <= end_date:
            is_quad = current.month in [3, 6, 9, 12]
            title = "Quadruple Witching" if is_quad else "Monthly Options Expiration"
            desc = "Simultaneous expiration of stock options and futures. Expect high volatility." if is_quad else "Standard monthly option contracts expire."
            events.append({
                "id": f"macro_opt_exp_{exp_date.strftime('%Y%m%d')}",
                "date": exp_date.isoformat(),
                "title": title,
                "type": "macro_event",
                "region": "US",
                "description": desc,
                "related_tickers": []
            })
        if current.month == 12: current = current.replace(year=current.year + 1, month=1)
        else: current = current.replace(month=current.month + 1)
    return events


def _derive_gdp_releases(start_date: date, end_date: date) -> List[dict]:
    events = []
    current = start_date.replace(day=1)
    while current <= end_date:
        # GDP releases are typically the last Thursday of every month
        gdp_date = _get_last_weekday(current.year, current.month, 3)
        if gdp_date and start_date <= gdp_date <= end_date:
            # Advance (Jan/Apr/Jul/Oct), Second (Feb/May/Aug/Nov), Final (Mar/Jun/Sep/Dec)
            phase = ["Final", "Advance", "Second", "Final", "Advance", "Second", "Final", "Advance", "Second", "Final", "Advance", "Second"][current.month - 1]
            events.append({
                "id": f"macro_gdp_{gdp_date.strftime('%Y%m%d')}",
                "date": gdp_date.isoformat(),
                "title": f"GDP {phase} Estimate",
                "type": "macro_event",
                "region": "US",
                "description": f"Bureau of Economic Analysis (BEA) releases the {phase} estimate of Gross Domestic Product for the previous quarter.",
                "related_tickers": []
            })
        if current.month == 12: current = current.replace(year=current.year + 1, month=1)
        else: current = current.replace(month=current.month + 1)
    return events


def _derive_bls_events(start_date: date, end_date: date) -> List[dict]:
    events = []
    # 1. Use hardcoded 2026 schedule for high precision
    if start_date.year <= 2026 <= end_date.year:
        for key, dates in BLS_2026_SCHEDULE.items():
            for d_str in dates:
                d = date.fromisoformat(d_str)
                if start_date <= d <= end_date:
                    title_map = {"NFP": "Non-Farm Payrolls (NFP)", "CPI": "Consumer Price Index (CPI)", "PPI": "Producer Price Index (PPI)"}
                    desc_map = {
                        "NFP": "Bureau of Labor Statistics (BLS) Employment Situation report. Key indicator of labor market health.",
                        "CPI": "Monthly inflation report. Measures price changes for consumers.",
                        "PPI": "Measures price changes from the perspective of costs to producers."
                    }
                    events.append({
                        "id": f"macro_{key.lower()}_{d.strftime('%Y%m%d')}",
                        "date": d.isoformat(),
                        "title": title_map[key],
                        "type": "macro_event",
                        "region": "US",
                        "description": desc_map[key],
                        "related_tickers": []
                    })
                    
    # 2. Fallback for other years (Simple Rule of Thumb)
    for year in range(start_date.year, end_date.year + 1):
        if year == 2026: continue # Handled above
        for month in range(1, 13):
            # NFP usually 1st Friday
            nfp = _get_nth_weekday(year, month, 4, 1)
            if nfp and start_date <= nfp <= end_date:
                events.append({"id": f"macro_nfp_{nfp.strftime('%Y%m%d')}", "date": nfp.isoformat(), "title": "Non-Farm Payrolls (NFP) [Est]", "type": "macro_event", "region": "US", "description": "Estimated release date for the BLS Employment Situation report."})
            # CPI usually 2nd Wednesday/Thursday
            cpi = _get_nth_weekday(year, month, 2, 2)
            if cpi and start_date <= cpi <= end_date:
                events.append({"id": f"macro_cpi_{cpi.strftime('%Y%m%d')}", "date": cpi.isoformat(), "title": "Consumer Price Index (CPI) [Est]", "type": "macro_event", "region": "US", "description": "Estimated release date for monthly consumer inflation gauge."})
                
    return events


def _derive_tax_day(start_date: date, end_date: date) -> List[dict]:
    events = []
    for year in range(start_date.year, end_date.year + 1):
        tax_date = date(year, 4, 15)
        if tax_date.weekday() == 5: tax_date += timedelta(days=2)
        elif tax_date.weekday() == 6: tax_date += timedelta(days=1)
        if start_date <= tax_date <= end_date:
            events.append({
                "id": f"macro_tax_day_{tax_date.strftime('%Y%m%d')}",
                "date": tax_date.isoformat(),
                "title": "US Tax Day",
                "type": "macro_event",
                "region": "US",
                "description": "Deadline for US individual income tax returns. Potential market liquidity impact.",
                "related_tickers": []
            })
    return events


def _derive_nio_adr_fee(start_date: date, end_date: date) -> List[dict]:
    events = []
    for year in range(start_date.year, end_date.year + 1):
        # NIO ADR record date is usually in January
        record_date = date(year, 1, 30) if year == 2024 else date(year, 1, 3)
        if start_date <= record_date <= end_date:
            events.append({
                "id": f"macro_nio_adr_fee_{record_date.strftime('%Y%m%d')}",
                "date": record_date.isoformat(),
                "title": "NIO ADR Fee Record Date",
                "type": "stock_event",
                "region": "US",
                "description": "Custodial/Pass-through fee record date for NIO ADR holders. Typically $0.02 per ADS.",
                "related_tickers": ["NIO"]
            })
    return events


def _extract_year_section(full_text, year):
    matches = list(re.finditer(r"(\d{4}) FOMC Meetings", full_text))
    positions = [(int(match.group(1)), match.start(), match.end()) for match in matches]
    for index, (matched_year, _, end_pos) in enumerate(positions):
        if matched_year != year: continue
        next_start = positions[index + 1][1] if index + 1 < len(positions) else len(full_text)
        return full_text[end_pos:next_start]
    return ""


def _fetch_fomc_events(start_date: date, end_date: date) -> List[dict]:
    try:
        response = requests.get(FOMC_CALENDAR_URL, timeout=20)
        response.encoding = "utf-8"
        text = BeautifulSoup(response.text, "html.parser").get_text("\n")
    except Exception as e:
        print(f"Error fetching FOMC calendar: {e}")
        return []

    events = []
    for year in range(start_date.year, end_date.year + 1):
        section = _extract_year_section(text, year)
        if not section: continue
        for m_name, s_day, e_day, has_sep in re.findall(r"([A-Z][a-z]+)\s+(\d{1,2})-(\d{1,2})(\*)?", section):
            m_num = MONTHS.get(m_name)
            if not m_num: continue
            d_date = date(year, m_num, int(e_day))
            if start_date <= d_date <= end_date:
                desc = "Federal Reserve FOMC meeting concludes with a policy decision."
                if has_sep: desc += " This meeting includes a Summary of Economic Projections (SEP)."
                events.append({"id": f"macro_fomc_{d_date.strftime('%Y%m%d')}", "date": d_date.isoformat(), "title": "FOMC Rate Decision", "type": "macro_event", "region": "US", "description": desc, "related_tickers": []})
    return events


def fetch_macro_events(start_date=None, end_date=None) -> List[dict]:
    res_start, res_end = _resolve_window(start_date, end_date)
    events = []
    events.extend(_fetch_fomc_events(res_start, res_end))
    events.extend(_derive_options_expirations(res_start, res_end))
    events.extend(_derive_bls_events(res_start, res_end))
    events.extend(_derive_gdp_releases(res_start, res_end))
    events.extend(_derive_tax_day(res_start, res_end))
    events.extend(_derive_nio_adr_fee(res_start, res_end))
    return events


if __name__ == "__main__":
    import json
    print(json.dumps(fetch_macro_events(), indent=2))
