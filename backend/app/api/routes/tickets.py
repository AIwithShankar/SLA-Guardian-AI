from fastapi import APIRouter

from app.schemas.ticket import TicketListResponse
from app.services.ticket_service import list_tickets

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=TicketListResponse)
def get_tickets() -> TicketListResponse:
    return list_tickets()
