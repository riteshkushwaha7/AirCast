from app.domain.activity_guidance import evaluate_activity_guidance
from app.utils.enums import ActivityType


def test_running_not_suitable_high_risk() -> None:
    guidance = evaluate_activity_guidance(ActivityType.RUNNING, "high")
    assert guidance.activity_suitable is False
    assert guidance.mask_advised is True


def test_commute_allowed_moderate_risk() -> None:
    guidance = evaluate_activity_guidance(ActivityType.COMMUTE, "moderate")
    assert guidance.activity_suitable is True
    assert guidance.avoid_outdoor is False
