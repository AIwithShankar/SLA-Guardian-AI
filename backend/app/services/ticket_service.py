from app.schemas.ticket import Ticket, TicketListResponse


def list_tickets() -> TicketListResponse:
    return TicketListResponse(
        source="mock",
        items=[
            Ticket(
                id="TKT-1001",
                subject="Unable to access account",
                priority="high",
                status="open",
                breach_risk=0.78,
            ),
            Ticket(
                id="TKT-1002",
                subject="Invoice question",
                priority="normal",
                status="pending",
                breach_risk=0.24,
            ),
        ],
    )
