# Market data pipeline

Downloads daily BTC, ETH and SOL prices from Yahoo Finance, validates them, and calculates per-symbol returns and annualized volatility.

```sh
pip install -e .
python -m pipeline.cli run
```

The command retries failed downloads, reports missing calendar days, writes partitioned prices to `data/prices`, features to `data/features.parquet`, and a volatility chart to `charts/vol_30d.png`. Invalid rows and their reasons are written to `data/quarantine.parquet`. If more than 5% of the downloaded rows fail validation, the quarantine is still written but the run stops before updating prices or features. Each run replaces the quarantine file. Prices are replaced by symbol/year partition, so previously stored partitions outside the current download remain.

## Tests

```sh
pip install -e . pytest ruff
ruff check .
pytest -q
```

Tests cover hand-calculated returns, symbol isolation, validation and missing dates. They do not cover real Yahoo Finance availability or API failures, nor do they establish the statistical quality of the derived features.
