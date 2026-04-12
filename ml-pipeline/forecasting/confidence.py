from typing import Literal

PlannerConfidence = Literal["higher confidence", "moderate confidence", "lower confidence"]


def compute_confidence_score(
    *,
    day_index: int,
    volatility: float,
    data_completeness: float = 1.0,
) -> float:
    bounded_day = max(0, min(day_index, 6))
    bounded_volatility = max(0.0, volatility)
    bounded_completeness = max(0.0, min(data_completeness, 1.0))

    score = 1.0
    score -= bounded_day * 0.11
    score -= min(0.32, bounded_volatility / 85.0)
    score += (bounded_completeness - 0.75) * 0.20
    return max(0.0, min(score, 1.0))


def confidence_label(
    *,
    day_index: int,
    volatility: float,
    data_completeness: float = 1.0,
) -> PlannerConfidence:
    score = compute_confidence_score(
        day_index=day_index,
        volatility=volatility,
        data_completeness=data_completeness,
    )
    if score >= 0.75:
        return "higher confidence"
    if score >= 0.45:
        return "moderate confidence"
    return "lower confidence"
