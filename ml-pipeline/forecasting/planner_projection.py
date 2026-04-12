from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

from forecasting.confidence import confidence_label
from shared.category_utils import aqi_to_category


@dataclass
class DailyPlannerProjection:
    date: str
    representative_aqi: float
    min_aqi: float
    max_aqi: float
    category: str
    trend: str
    confidence_label: str


def project_weekly_daily_aqi(
    *,
    recent_series: pd.Series,
    start_date: date,
    days: int = 7,
) -> list[DailyPlannerProjection]:
    if recent_series.empty:
        baseline = 140.0
        volatility = 18.0
    else:
        numeric = pd.to_numeric(recent_series, errors="coerce").dropna()
        baseline = float(numeric.tail(24).mean()) if not numeric.empty else 140.0
        volatility = float(numeric.tail(72).std(ddof=0)) if len(numeric) > 3 else 14.0

    drift = _estimate_drift(recent_series)
    projections: list[DailyPlannerProjection] = []
    previous_value: float | None = None

    for index in range(days):
        projected = max(0.0, baseline + drift * index + _seasonal_component(index))
        spread = 15.0 + min(index, 6) * 2.5
        min_aqi = max(0.0, projected - spread)
        max_aqi = max(min_aqi, projected + spread)
        trend = _trend(previous_value, projected)
        projections.append(
            DailyPlannerProjection(
                date=(start_date + timedelta(days=index)).isoformat(),
                representative_aqi=round(projected, 1),
                min_aqi=round(min_aqi, 1),
                max_aqi=round(max_aqi, 1),
                category=aqi_to_category(projected),
                trend=trend,
                confidence_label=confidence_label(
                    day_index=index,
                    volatility=volatility,
                    data_completeness=0.95 if index <= 2 else 0.82,
                ),
            )
        )
        previous_value = projected
    return projections


def _estimate_drift(series: pd.Series) -> float:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric) < 12:
        return 0.0
    recent = float(numeric.tail(12).mean())
    older = float(numeric.tail(24).head(12).mean()) if len(numeric) >= 24 else float(numeric.head(12).mean())
    delta = recent - older
    return max(-8.0, min(8.0, delta / 4.0))


def _seasonal_component(day_index: int) -> float:
    return float(np.sin(day_index / 2.0) * 4.0)


def _trend(previous_value: float | None, current_value: float) -> str:
    if previous_value is None:
        return "stable"
    delta = current_value - previous_value
    if delta >= 10:
        return "worsening"
    if delta <= -10:
        return "improving"
    return "stable"
