from app.schemas.planner import PlannerConfidence


def confidence_from_horizon(
    *,
    day_index: int,
    volatility: float = 0.0,
    data_completeness: float = 1.0,
    model_quality: float = 0.75,
) -> PlannerConfidence:
    """Map horizon + data quality signals into simple planner confidence labels."""
    bounded_index = max(0, min(day_index, 6))
    bounded_volatility = max(0.0, volatility)
    bounded_completeness = max(0.0, min(data_completeness, 1.0))
    bounded_quality = max(0.0, min(model_quality, 1.0))

    score = 1.0
    score -= bounded_index * 0.10
    score -= min(0.30, bounded_volatility / 90.0)
    score += (bounded_completeness - 0.8) * 0.25
    score += (bounded_quality - 0.7) * 0.20

    if score >= 0.76:
        return "higher confidence"
    if score >= 0.48:
        return "moderate confidence"
    return "lower confidence"
