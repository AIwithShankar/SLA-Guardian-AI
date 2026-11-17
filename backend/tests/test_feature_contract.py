import pytest

from ml.feature_contract import FeatureContractError, validate_features


VALID_FEATURES = {
    "priority": "3 - Moderate",
    "category": "Category 40",
    "ticket_age_hours": 1.5,
    "remaining_sla_hours": 22.5,
    "created_hour": 9,
    "created_weekday": 2,
}


def test_validate_features_returns_approved_order_and_normalizes_category() -> None:
    result = validate_features({**VALID_FEATURES, "category": "?"})

    assert list(result) == [
        "priority",
        "category",
        "ticket_age_hours",
        "remaining_sla_hours",
        "created_hour",
        "created_weekday",
    ]
    assert result["category"] == "Unknown"


@pytest.mark.parametrize(
    "change",
    [
        {"ticket_age_hours": -0.1},
        {"remaining_sla_hours": 72.1},
        {"created_hour": 24},
        {"created_weekday": 7},
        {"ticket_age_hours": float("nan")},
    ],
)
def test_validate_features_rejects_invalid_numeric_values(change) -> None:
    features = {**VALID_FEATURES, **change}

    with pytest.raises(FeatureContractError):
        validate_features(features)


def test_validate_features_rejects_metadata_and_missing_fields() -> None:
    with pytest.raises(FeatureContractError):
        validate_features({**VALID_FEATURES, "ticket_id": "INC0000045"})

    incomplete = dict(VALID_FEATURES)
    del incomplete["category"]
    with pytest.raises(FeatureContractError):
        validate_features(incomplete)
