import pandas as pd


class FeatureService:
    """Feature engineering helpers for AQI time-series."""

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        features = df.copy()
        if features.empty:
            return features

        features = self.add_temporal_features(features)
        features = self.add_rolling_features(features)
        features = self.add_lag_features(features)
        return features

    def add_temporal_features(self, df: pd.DataFrame, time_col: str = "observed_at") -> pd.DataFrame:
        features = df.copy()
        ts = pd.to_datetime(features[time_col], utc=True)
        features["hour_of_day"] = ts.dt.hour.astype(int)
        features["day_of_week"] = ts.dt.dayofweek.astype(int)
        features["is_weekend"] = (features["day_of_week"] >= 5).astype(int)
        return features

    def add_rolling_features(self, df: pd.DataFrame, value_col: str = "aqi") -> pd.DataFrame:
        features = df.copy()
        features["rolling_avg_3h"] = features[value_col].rolling(window=3, min_periods=1).mean()
        features["rolling_avg_6h"] = features[value_col].rolling(window=6, min_periods=1).mean()
        features["rolling_avg_12h"] = features[value_col].rolling(window=12, min_periods=1).mean()
        return features

    def add_lag_features(self, df: pd.DataFrame, value_col: str = "aqi") -> pd.DataFrame:
        features = df.copy()
        lag_windows = [1, 3, 6, 12, 24]
        for lag in lag_windows:
            features[f"lag_{lag}"] = features[value_col].shift(lag)
        return features
