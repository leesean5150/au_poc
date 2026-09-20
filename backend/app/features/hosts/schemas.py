from pydantic import BaseModel

from app.core.schemas import HostProfileOut, InvitationOut

__all__ = ["HostProfileOut", "HostRow", "HostDetail", "HostFilters"]


class HostRow(HostProfileOut):
    guest_count: int
    by_status: dict[str, int]


class HostDetail(BaseModel):
    host: HostProfileOut
    invitations: list[InvitationOut]


class HostFilters(BaseModel):
    event_id: int | None = None
    department: str | None = None
    search: str | None = None
    sort: str = "name"
    order: str = "asc"
