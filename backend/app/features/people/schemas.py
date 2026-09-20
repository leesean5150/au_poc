from pydantic import BaseModel, ConfigDict

from app.core.schemas import GuestProfileOut, InvitationOut

__all__ = ["GuestProfileOut", "PersonRow", "PersonDetail", "PersonPatch", "PersonFilters"]


class PersonRow(GuestProfileOut):
    invitation_count: int


class PersonDetail(BaseModel):
    person: GuestProfileOut
    invitations: list[InvitationOut]


class PersonPatch(BaseModel):
    """Identity fields — invitation fields are edited via PATCH /api/invitations."""

    model_config = ConfigDict(extra="forbid")

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    title: str | None = None
    company: str | None = None
    job_title: str | None = None
    guest_type: str | None = None
    city_of_residence: str | None = None


class PersonFilters(BaseModel):
    search: str | None = None
    sort: str = "name"
    order: str = "asc"
