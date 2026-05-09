from app.domain.confidence_labels import confidence_from_horizon


def test_confidence_labels_reduce_with_horizon_and_volatility() -> None:
    near_term = confidence_from_horizon(day_index=0, volatility=4)
    medium_term = confidence_from_horizon(day_index=3, volatility=22)
    long_term = confidence_from_horizon(day_index=6, volatility=75)

    assert near_term == "higher confidence"
    assert medium_term in {"higher confidence", "moderate confidence"}
    assert long_term == "lower confidence"
