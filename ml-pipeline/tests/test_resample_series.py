import pandas as pd

from preprocessing.resample_series import resample_dataframe


def test_resample_marks_imputed_rows() -> None:
    df = pd.DataFrame(
        {
            "observed_at": [
                "2026-04-07T00:00:00Z",
                "2026-04-07T01:00:00Z",
                "2026-04-07T03:00:00Z",
            ],
            "aqi": [165, 171, 178],
        }
    )
    out = resample_dataframe(df, short_gap_limit=2, strategy="ffill_then_interp")

    row_for_gap = out[out["observed_at"] == pd.Timestamp("2026-04-07T02:00:00Z")]
    assert not row_for_gap.empty
    assert int(row_for_gap.iloc[0]["missing_flag"]) == 1
    assert int(row_for_gap.iloc[0]["imputed_flag"]) == 1
