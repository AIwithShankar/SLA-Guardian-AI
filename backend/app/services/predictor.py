"""Research-model inference boundary with process-local lazy loading."""

from __future__ import annotations

import math
from collections.abc import Mapping
from functools import lru_cache
from threading import Lock
from typing import Any, Protocol

MODEL_VERSION = "phase4_research_v1"


class Predictor(Protocol):
    def predict_probability(self, features: Mapping[str, Any]) -> float:
        ...


class PredictionUnavailable(RuntimeError):
    """Raised when the trusted research model cannot provide inference."""


@lru_cache(maxsize=1)
def _load_model_once() -> Any:
    try:
        from ml.artifact_loader import load_trusted_model

        return load_trusted_model()
    except (
        AttributeError,
        ImportError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        raise PredictionUnavailable("research model is unavailable") from error


class TrustedModelPredictor:
    """Load the approved model at most once per application process."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._lock = Lock()

    def _get_model(self) -> Any:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._model = _load_model_once()
        return self._model

    def predict_probability(self, features: Mapping[str, Any]) -> float:
        try:
            import pandas as pd

            model = self._get_model()
            probability = float(
                model.predict_proba(pd.DataFrame([dict(features)]))[0][1]
            )
        except PredictionUnavailable:
            raise
        except (
            AttributeError,
            ImportError,
            IndexError,
            KeyError,
            OSError,
            TypeError,
            ValueError,
        ) as error:
            raise PredictionUnavailable("research model inference failed") from error
        if not math.isfinite(probability) or not 0 <= probability <= 1:
            raise PredictionUnavailable("research model returned an invalid probability")
        return probability
