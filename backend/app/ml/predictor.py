from app.schemas.prediction import PredictionRequest, PredictionResponse


def predict(payload: PredictionRequest) -> PredictionResponse:
    """Return a deterministic mock until a trained model is configured."""
    score = 0.65 if payload.priority.lower() in {"high", "urgent"} else 0.25
    return PredictionResponse(
        ticket_id=payload.ticket_id,
        breach_probability=score,
        will_breach=score >= 0.5,
        model_status="mock",
        explanation=["No trained model configured", "Priority used as mock signal"],
    )
