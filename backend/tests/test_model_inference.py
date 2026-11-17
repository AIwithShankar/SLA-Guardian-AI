import importlib.util
import math
import sys

import pytest

from ml.artifact_loader import load_trusted_model
from ml.feature_contract import validate_features


RUNTIME_MODULES = ("joblib", "numpy", "pandas", "sklearn", "lightgbm")
MISSING_MODULES = [
    name for name in RUNTIME_MODULES if importlib.util.find_spec(name) is None
]

pytestmark = pytest.mark.skipif(
    sys.version_info[:2] != (3, 13) or MISSING_MODULES,
    reason=(
        "requires the isolated Python 3.13 research runtime with "
        "recorded inference dependencies"
    ),
)


def test_trusted_model_returns_stable_probability() -> None:
    import pandas as pd

    features = validate_features(
        {
            "priority": "3 - Moderate",
            "category": "Category 40",
            "ticket_age_hours": 1.5,
            "remaining_sla_hours": 22.5,
            "created_hour": 9,
            "created_weekday": 2,
        }
    )
    model = load_trusted_model()
    frame = pd.DataFrame([features])

    first_probability = float(model.predict_proba(frame)[0][1])
    second_probability = float(model.predict_proba(frame)[0][1])

    assert math.isfinite(first_probability)
    assert 0.0 <= first_probability <= 1.0
    assert second_probability == first_probability
