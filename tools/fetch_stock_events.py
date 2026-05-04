import yfinance as yf
from datetime import date, datetime

from tools.event_config import get_tracked_tickers


def _normalize_to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if hasattr(value, "to_pydatetime"):
        return value.to_pydatetime().date()
    return None


def fetch_stock_events(tickers=None):
    tickers = tickers or get_tracked_tickers()
    events = []
    for ticker_symbol in tickers:
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch Next Earnings Date
            calendar = ticker.calendar
            if calendar is not None:
                # yfinance calendar can be a dict or DataFrame.
                if isinstance(calendar, dict) and 'Earnings Date' in calendar:
                    dates = calendar['Earnings Date']
                    for d in dates:
                        normalized_date = _normalize_to_date(d)
                        if normalized_date:
                            events.append({
                                "id": f"earn_{ticker_symbol}_{normalized_date.strftime('%Y%m%d')}",
                                "date": normalized_date.strftime("%Y-%m-%d"),
                                "title": f"{ticker_symbol} Earnings",
                                "type": "stock_event",
                                "region": "US",
                                "description": f"Earnings report for {ticker_symbol}",
                                "related_tickers": [ticker_symbol]
                            })
                elif hasattr(calendar, 'empty') and not calendar.empty and 'Earnings Date' in calendar:
                    dates = calendar['Earnings Date']
                    for d in dates:
                        normalized_date = _normalize_to_date(d)
                        if normalized_date:
                            events.append({
                                "id": f"earn_{ticker_symbol}_{normalized_date.strftime('%Y%m%d')}",
                                "date": normalized_date.strftime("%Y-%m-%d"),
                                "title": f"{ticker_symbol} Earnings",
                                "type": "stock_event",
                                "region": "US",
                                "description": f"Earnings report for {ticker_symbol}",
                                "related_tickers": [ticker_symbol]
                            })
                            
            # Fetch Recent Dividends
            dividends = ticker.dividends
            if dividends is not None and not dividends.empty:
                # Get the last few dividends
                recent = dividends.tail(3)
                for date, amount in recent.items():
                    events.append({
                        "id": f"div_{ticker_symbol}_{date.strftime('%Y%m%d')}",
                        "date": date.strftime("%Y-%m-%d"),
                        "title": f"{ticker_symbol} Dividend (${amount:.2f})",
                        "type": "stock_event",
                        "region": "US",
                        "description": f"Dividend payment of ${amount:.2f} for {ticker_symbol}",
                        "related_tickers": [ticker_symbol]
                    })

            if isinstance(calendar, dict):
                for field_name, label in (
                    ("Dividend Date", "Dividend Date"),
                    ("Ex-Dividend Date", "Ex-Dividend Date"),
                ):
                    normalized_date = _normalize_to_date(calendar.get(field_name))
                    if normalized_date:
                        events.append({
                            "id": f"{field_name.lower().replace('-', '').replace(' ', '_')}_{ticker_symbol}_{normalized_date.strftime('%Y%m%d')}",
                            "date": normalized_date.strftime("%Y-%m-%d"),
                            "title": f"{ticker_symbol} {label}",
                            "type": "stock_event",
                            "region": "US",
                            "description": f"{label} for {ticker_symbol}",
                            "related_tickers": [ticker_symbol]
                        })
                    
        except Exception as e:
            print(f"Error fetching events for {ticker_symbol}: {e}")
            
    return events

if __name__ == "__main__":
    import json
    print(json.dumps(fetch_stock_events(), indent=2))
