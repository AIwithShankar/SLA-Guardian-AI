from pydantic import BaseModel


class Ticket(BaseModel):
    id: str
    subject: str
    priority: str
    status: str
    breach_risk: float


class TicketListResponse(BaseModel):
    items: list[Ticket]
    source: str
