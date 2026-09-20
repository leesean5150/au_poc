"""Shared read representations of the four tables.

These are as shared as `models.py`: several slices return a person / host /
event / flattened-guest shape, and it must be one definition so the wire
contract can't drift. Slice-specific schemas (filters, patches, rows with
aggregates, detail envelopes) live in each feature's own `schemas.py`.
"""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, computed_field


def _to_str_id(v: object) -> object:
    return v if v is None else str(v)


IdStr = Annotated[str, BeforeValidator(_to_str_id)]


class ORMModel(BaseModel):
    """Base for response models read straight off SQLAlchemy rows."""

    model_config = ConfigDict(from_attributes=True)


class UserOut(ORMModel):
    id: IdStr
    first_name: str | None
    last_name: str | None
    email: str


class GuestProfileOut(ORMModel):
    user: UserOut
    title: str | None
    company: str | None
    job_title: str | None
    guest_type: str
    city_of_residence: str | None


class HostProfileOut(ORMModel):
    user: UserOut
    city_of_residence: str | None
    department: str | None


class EventOut(ORMModel):
    id: IdStr
    name: str
    starts_on: date
    ends_on: date | None
    location: str | None


class InvitationOut(ORMModel):
    """An invitation flattened with its guest, host and event."""

    id: IdStr
    guest_user_id: IdStr
    host_user_id: IdStr
    event_id: IdStr

    registration_type: str | None
    group_name: str | None
    business_case: str | None
    compliance_approved: bool | None
    status: str

    requires_flights: bool | None
    flight_class: str | None
    departure_city: str | None
    requires_airport_transfer: bool | None
    transfer_type: str | None
    requires_accommodation: bool | None
    check_in_date: date | None
    check_out_date: date | None

    workshop: str | None
    additional_experience: str | None
    sightseeing_contact_email: str | None
    additional_information: str | None

    guest: GuestProfileOut
    host: HostProfileOut
    event: EventOut

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        parts = [self.guest.user.first_name, self.guest.user.last_name]
        return " ".join(p for p in parts if p) or "(unnamed)"
