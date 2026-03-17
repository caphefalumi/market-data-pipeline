"""Run the market data pipeline with ``python -m pipeline.cli run``."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from pipeline.features import add_features
from pipeline.ingest import fetch_prices
from pipeline.storage import read_prices, write_parquet, write_prices
from pipeline.validate import DataValidationError, find_gaps, validate_prices


def run():
    prices = fetch_prices()
    try:
        clean, quarantined = validate_prices(prices)
    except DataValidationError as error:
        write_parquet(error.quarantined, "data/quarantine.parquet")
        raise
    write_parquet(quarantined, "data/quarantine.parquet")
    gaps = find_gaps(clean)
    if not gaps.empty:
        print(f"Warning: {len(gaps)} missing symbol-days in validated prices")
    write_prices(clean)
    features = add_features(read_prices())
    write_parquet(features, "data/features.parquet")
    vol = features.pivot(index="date", columns="symbol", values="vol_30d")
    ax = vol.plot(figsize=(10, 5), title="30-day annualized volatility")
    ax.set_ylabel("Volatility")
    plt.tight_layout()
    Path("charts").mkdir(parents=True, exist_ok=True)
    plt.savefig("charts/vol_30d.png", dpi=150)
    plt.close()
    print(f"Wrote {len(clean)} rows for {clean['symbol'].nunique()} symbols")
    print(features.groupby("symbol", observed=True)[["return_30d", "vol_30d"]].describe().T)


def main():
    parser = argparse.ArgumentParser(description="Crypto market data pipeline")
    parser.add_argument("command", choices=["run"])
    parser.parse_args()
    run()


if __name__ == "__main__":
    main()
