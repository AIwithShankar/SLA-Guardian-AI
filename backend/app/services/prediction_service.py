from app.ml.predictor import predict
from app.schemas.prediction import PredictionRequest, PredictionResponse


def predict_sla_breach(payload: PredictionRequest) -> PredictionResponse:
    return predict(payload)
