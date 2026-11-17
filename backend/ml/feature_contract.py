"""Validation for the Phase 4 research model's approved feature contract."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Real
from typing import Any

APPROVED_FEATURES = (
    "priority",
    "category",
    "ticket_age_hours",
    "remaining_sla_hours",
    "created_hour",
    "created_weekday",
)

CATEGORICAL_FEATURES = frozenset(("priority", "category"))
NUMERIC_RANGES = {
    "ticket_age_hours": (0.0, 72.0),
    "remaining_sla_hours": (0.0, 72.0),
    "created_hour": (0.0, 23.0),
    "created_weekday": (0.0, 6.0),
}


def normalize_categorical_frame(frame: Any) -> Any:
    """Apply the categorical normalization used by the research pipeline."""

    normalized = frame.copy()
    if "category" in normalized.columns:
        normalized["category"] = normalized["category"].replace(
            {"?": "Unknown", "": "Unknown"}
        )
    return normalized


class FeatureContractError(ValueError):
    """Raised when input does not match the approved model feature contract."""


def _validate_row(features: Mapping[str, Any]) -> dict[str, Any]:
    expected = set(APPROVED_FEATURES)
    received = set(features)
    missing = expected - received
    extra = received - expected
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing features: {sorted(missing)}")
        if extra:
            details.append(f"unsupported features: {sorted(extra)}")
        raise FeatureContractError("; ".join(details))

    validated: dict[str, Any] = {}
    for name in APPROVED_FEATURES:
        value = features[name]
        if name in CATEGORICAL_FEATURES:
            if not isinstance(value, str):
                raise FeatureContractError(
                    f"{name} must be a non-empty string"
                )
            if name == "category" and value in {"", "?"}:
                value = "Unknown"
            if not value:
                raise FeatureContractError(
                    f"{name} must be a non-empty string"
                )
            validated[name] = value
            continue

        if isinstance(value, bool) or not isinstance(value, Real):
            raise FeatureContractError(f"{name} must be a finite number")
        numeric_value = float(value)
        lower, upper = NUMERIC_RANGES[name]
        if not math.isfinite(numeric_value) or not lower <= numeric_value <= upper:
            raise FeatureContractError(
                f"{name} must be between {lower} and {upper}, inclusive"
            )
        validated[name] = numeric_value

    return validated


def validate_features(
    features: Mapping[str, Any] | Sequence[Mapping[str, Any]],
) -> dict[str, Any] | list[dict[str, Any]]:
    """Validate one feature row or a batch without accepting metadata fields."""

    if isinstance(features, Mapping):
        return _validate_row(features)
    if isinstance(features, (str, bytes)) or not isinstance(features, Sequence):
        raise FeatureContractError("features must be a mapping or a sequence of mappings")
    return [_validate_row(row) for row in features]
