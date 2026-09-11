from pydantic import BaseModel, ConfigDict

from app.core.schemas import GuestOut, PersonOut

__all__ = ["PersonOut", "PersonRow", "PersonDetail", "PersonPatch", "PersonFilters"]


class PersonRow(PersonOut):
    invitation_count: int


class PersonDetail(BaseModel):
    person: PersonOut
    invitations: list[GuestOut]


class PersonPatch(BaseModel):
    """Identity fields only — invitation fields are edited via PATCH /api/guests."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    work_email: str | None = None
    company: str | None = None
    job_title: str | None = None
    guest_type: str | None = None
    city_of_residence: str | None = None


class PersonFilters(BaseModel):
    search: str | None = None
    sort: str = "name"
    order: str = "asc"
