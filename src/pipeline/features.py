"""Calculate per-symbol returns and annualized rolling volatility."""

import numpy as np


def add_features(df, windows=(7, 30)):
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True).copy()
    by_symbol = df.groupby("symbol", observed=True)
    df["daily_return"] = by_symbol["close"].pct_change(fill_method=None)
    for window in windows:
        df[f"return_{window}d"] = by_symbol["close"].pct_change(window, fill_method=None)
        df[f"vol_{window}d"] = (
            df.groupby("symbol", observed=True)["daily_return"]
            .transform(lambda returns, window=window: returns.rolling(window).std())
            * np.sqrt(365)
        )
    return df
