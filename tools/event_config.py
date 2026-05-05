import os
from typing import List

DEFAULT_TICKERS = ["NIO", "NVDA", "TSLA"]

CN_PUBLIC_HOLIDAYS_URL = "https://www.gov.cn/zhengce/zhengceku/202511/content_7047091.htm?sourcefrom=aladdin"
HK_PUBLIC_HOLIDAYS_URL = "https://www.info.gov.hk/gia/general/202505/16/P2025051300353p.htm"
US_PUBLIC_HOLIDAYS_URL = "https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/"
US_MARKET_HOLIDAYS_URL = "https://www.nyse.com/markets/hours-calendars"
HKO_SOLAR_TERMS_XML_URL_TEMPLATE = "https://www.hko.gov.hk/en/gts/astronomy/data/files/24SolarTerms_{year}.xml"


def get_tracked_tickers() -> List[str]:
    raw_tickers = os.getenv("STOCK_CALENDAR_TICKERS", "")
    if not raw_tickers.strip():
        return list(DEFAULT_TICKERS)

    tickers = [ticker.strip().upper() for ticker in raw_tickers.split(",") if ticker.strip()]
    return tickers or list(DEFAULT_TICKERS)
