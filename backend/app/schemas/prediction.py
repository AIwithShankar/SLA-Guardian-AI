from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    ticket_id: str = Field(min_length=1)
    priority: str = "normal"


class PredictionResponse(BaseModel):
    ticket_id: str
    breach_probability: float
    will_breach: bool
    model_status: str
    explanation: list[str]
