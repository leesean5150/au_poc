from datetime import date

from pydantic import BaseModel

from app.core.schemas import IdStr, ORMModel


class StatsEvent(ORMModel):
    id: IdStr
    name: str
    starts_on: date
    ends_on: date | None


class ComplianceBreakdown(BaseModel):
    approved: int
    rejected: int
    pending: int


class LogisticsBreakdown(BaseModel):
    need_flights: int
    need_accommodation: int
    need_transfer: int


class NextEvent(BaseModel):
    name: str
    starts_on: date
    days_until: int


class UpcomingEvent(BaseModel):
    name: str
    starts_on: date
    days_until: int


class StatsOverview(BaseModel):
    event: StatsEvent
    total_guests: int
    by_status: dict[str, int]
    invites_sent: int
    invites_outstanding: int
    ready_to_send: int
    blocked_on_info: int
    acceptance_rate: float | None
    compliance: ComplianceBreakdown
    logistics: LogisticsBreakdown
    next_event: NextEvent | None
    upcoming_events: list[UpcomingEvent]
    guests_by_department: dict[str, int]
    guests_by_type: dict[str, int]
