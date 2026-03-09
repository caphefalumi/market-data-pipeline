"""Download daily crypto prices."""

import time

import pandas as pd
import yfinance as yf

TICKERS = ("BTC-USD", "ETH-USD", "SOL-USD")
START = "2023-01-01"


def fetch_prices(tickers=TICKERS, start=START, attempts=3):
    frames = []
    for ticker in tickers:
        for attempt in range(attempts):
            try:
                history = yf.Ticker(ticker).history(start=start, auto_adjust=True, raise_errors=True)
                if history.empty:
                    raise ValueError(f"No prices returned for {ticker}")
                break
            except Exception:
                if attempt == attempts - 1:
                    raise
                time.sleep(2**attempt)
        frame = history.reset_index()[["Date", "Close", "Volume"]]
        frame.columns = ["date", "close", "volume"]
        frame["date"] = pd.to_datetime(frame["date"]).dt.tz_localize(None).dt.normalize()
        frame["symbol"] = ticker
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)
