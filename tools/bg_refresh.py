import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import logging
from datetime import datetime, timedelta

from tools.db import init_db, upsert_events
from tools.fetch_holidays import fetch_market_holidays
from tools.fetch_macro_events import fetch_macro_events
from tools.fetch_public_holidays import fetch_public_holidays
from tools.fetch_stock_events import fetch_stock_events

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_refresh():
    logging.info("Starting background refresh job...")
    init_db()
    
    # We fetch a wide range for background caching:
    # previous year, current year, and next year.
    current_year = datetime.now().year
    start_date = datetime(current_year - 1, 1, 1).date()
    end_date = datetime(current_year + 1, 12, 31).date()
    
    all_events = []
    
    try:
        logging.info("Fetching market holidays...")
        holidays = fetch_market_holidays(start_date=start_date, end_date=end_date)
        all_events.extend(holidays)
    except Exception as e:
        logging.error(f"Error fetching market holidays: {e}")

    try:
        logging.info("Fetching public holidays...")
        pub_holidays = fetch_public_holidays(start_date=start_date, end_date=end_date)
        all_events.extend(pub_holidays)
    except Exception as e:
        logging.error(f"Error fetching public holidays: {e}")

    try:
        logging.info("Fetching stock events...")
        # Note: Tickers are read from env in the fetch tool or defaulted inside it.
        stock_events = fetch_stock_events()
        all_events.extend(stock_events)
    except Exception as e:
        logging.error(f"Error fetching stock events: {e}")

    try:
        logging.info("Fetching macro events...")
        macro_events = fetch_macro_events(start_date=start_date, end_date=end_date)
        all_events.extend(macro_events)
    except Exception as e:
        logging.error(f"Error fetching macro events: {e}")

    if all_events:
        upsert_events(all_events)
        logging.info(f"Successfully upserted {len(all_events)} events into the database.")
    else:
        logging.warning("No events were fetched to upsert.")

if __name__ == "__main__":
    run_refresh()
