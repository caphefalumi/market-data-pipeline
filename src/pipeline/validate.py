"""Validate price records and report missing calendar days."""

import pandas as pd


class DataValidationError(Exception):
    """Too many records failed validation; quarantined records are attached."""

    def __init__(self, message, quarantined):
        super().__init__(message)
        self.quarantined = quarantined


def validate_prices(df: pd.DataFrame, max_daily_move: float = 0.5):
    """Return clean and quarantined records; reject batches over 5% invalid."""
    df = df.sort_values(["symbol", "date"], kind="stable").reset_index(drop=True)
    returns = df.groupby("symbol")["close"].pct_change(fill_method=None)
    reasons = pd.Series("", index=df.index)
    reasons.loc[df["close"].isna()] += "null_close;"
    reasons.loc[df["close"] <= 0] += "non_positive_close;"
    reasons.loc[df.duplicated(["symbol", "date"], keep="first")] += "duplicate;"
    reasons.loc[returns.abs() > max_daily_move] += "extreme_move;"
    bad = reasons.ne("")
    quarantined = df.loc[bad].assign(reason=reasons.loc[bad])
    if len(df) and bad.mean() > 0.05:
        raise DataValidationError(f"{bad.mean():.1%} of rows failed validation", quarantined)
    return df.loc[~bad].copy(), quarantined


def find_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing calendar days within each symbol's observed date range."""
    missing = []
    for symbol, group in df.groupby("symbol", observed=True):
        dates = pd.to_datetime(group["date"])
        full = pd.date_range(dates.min(), dates.max(), freq="D")
        missing.extend((symbol, date) for date in full.difference(dates))
    return pd.DataFrame(missing, columns=["symbol", "missing_date"])
