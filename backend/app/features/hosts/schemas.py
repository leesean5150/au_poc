from pydantic import BaseModel

from app.core.schemas import GuestOut, HostOut

__all__ = ["HostOut", "HostRow", "HostDetail", "HostFilters"]


class HostRow(HostOut):
    guest_count: int
    by_status: dict[str, int]


class HostDetail(BaseModel):
    host: HostOut
    invitations: list[GuestOut]


class HostFilters(BaseModel):
    event_id: int | None = None
    department: str | None = None
    search: str | None = None
    sort: str = "name"
    order: str = "asc"
