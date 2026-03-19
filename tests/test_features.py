import pandas as pd
import pytest

from pipeline.features import add_features


def test_rolling_return_known_values():
    df = pd.DataFrame({
        "symbol": ["A"] * 3,
        "date": pd.date_range("2024-01-01", periods=3),
        "close": [100.0, 110.0, 121.0],
    })
    out = add_features(df, windows=(1,))
    assert out["return_1d"].iloc[1] == pytest.approx(0.10)
    assert out["return_1d"].iloc[2] == pytest.approx(0.10)


def test_features_do_not_mix_symbols():
    df = pd.DataFrame({
        "symbol": ["A", "B"], "date": pd.to_datetime(["2024-01-01"] * 2),
        "close": [100.0, 5.0],
    })
    assert add_features(df, windows=(1,))["return_1d"].isna().all()
