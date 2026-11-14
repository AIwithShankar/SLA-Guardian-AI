from fastapi import APIRouter

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import predict_sla_breach

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("", response_model=PredictionResponse)
def create_prediction(payload: PredictionRequest) -> PredictionResponse:
    return predict_sla_breach(payload)
