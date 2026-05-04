import akshare as ak
import yfinance as yf
import sys

def test_akshare():
    print("Testing Akshare (A-share Trade Calendar)...")
    try:
        # Get trade calendar for A-shares
        trade_date_df = ak.tool_trade_date_hist_sina()
        if not trade_date_df.empty:
            print(f"Success! Retrieved {len(trade_date_df)} trading days.")
            print(trade_date_df.head(3))
        else:
            print("Failed: Empty DataFrame returned.")
            sys.exit(1)
    except Exception as e:
        print(f"Akshare Error: {e}")
        sys.exit(1)

def test_yfinance():
    print("\nTesting Yfinance (AAPL Info)...")
    try:
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if 'shortName' in info:
            print(f"Success! Retrieved info for {info['shortName']}")
        else:
            print("Failed: Could not retrieve ticker info.")
            sys.exit(1)
    except Exception as e:
        print(f"Yfinance Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_akshare()
    test_yfinance()
    print("\nAll data sources verified successfully.")
