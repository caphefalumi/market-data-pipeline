"""Parquet persistence for prices and derived datasets."""

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def write_prices(df, path="data/prices"):
    prices = df.copy()
    prices["year"] = prices["date"].dt.year
    pq.write_to_dataset(
        pa.Table.from_pandas(prices, preserve_index=False),
        root_path=str(path),
        partition_cols=["symbol", "year"],
        existing_data_behavior="delete_matching",
    )


def read_prices(path="data/prices"):
    return pd.read_parquet(path)


def write_parquet(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
