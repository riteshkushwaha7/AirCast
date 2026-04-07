import pandas as pd

from app.services.feature_service import FeatureService


def test_feature_generation_columns() -> None:
    timestamps = pd.date_range("2026-04-01T00:00:00Z", periods=30, freq="h")
    df = pd.DataFrame({"observed_at": timestamps, "aqi": [120 + (idx % 10) for idx in range(len(timestamps))]})

    service = FeatureService()
    out = service.build_features(df)

    expected_columns = {
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "rolling_avg_3h",
        "rolling_avg_6h",
        "rolling_avg_12h",
        "lag_1",
        "lag_3",
        "lag_6",
        "lag_12",
        "lag_24",
    }
    assert expected_columns.issubset(set(out.columns))
    assert len(out) == len(df)
