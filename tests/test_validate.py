import pandas as pd
import pytest

from pipeline.validate import DataValidationError, find_gaps, validate_prices


def test_validation_quarantines_bad_records():
    dates = list(pd.date_range("2024-01-01", periods=100))
    df = pd.DataFrame({"symbol": "A", "date": dates, "close": 100.0})
    df.loc[10, "close"] = -10.0
    df.loc[30, "close"] = 190.0
    df.loc[50, "date"] = df.loc[49, "date"]
    clean, bad = validate_prices(df)
    assert len(clean) + len(bad) == len(df)
    assert "non_positive_close;" in bad.loc[bad["date"] == dates[10], "reason"].iloc[0]
    assert "extreme_move;" in bad.loc[bad["date"] == dates[30], "reason"].iloc[0]
    assert bad["reason"].str.contains("duplicate;").any()


def test_too_many_bad_records_are_attached_to_error():
    df = pd.DataFrame({"symbol": ["A"], "date": pd.to_datetime(["2024-01-01"]), "close": [-1.0]})
    with pytest.raises(DataValidationError) as error:
        validate_prices(df)
    assert error.value.quarantined["reason"].iloc[0] == "non_positive_close;"


def test_find_gaps_per_symbol():
    df = pd.DataFrame({"symbol": ["A", "A", "B"], "date": pd.to_datetime([
        "2024-01-01", "2024-01-03", "2024-01-02",
    ])})
    gaps = find_gaps(df)
    assert gaps.to_dict("records") == [{"symbol": "A", "missing_date": pd.Timestamp("2024-01-02")}]
