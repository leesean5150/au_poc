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


class PersonOut(ORMModel):
    id: IdStr
    title: str | None
    first_name: str | None
    last_name: str | None
    work_email: str | None
    company: str | None
    job_title: str | None
    guest_type: str
    city_of_residence: str | None


class HostOut(ORMModel):
    id: IdStr
    first_name: str | None
    last_name: str | None
    email: str | None
    city_of_residence: str | None
    department: str | None


class EventOut(ORMModel):
    id: IdStr
    name: str
    event_type: str
    starts_on: date
    ends_on: date | None
    location: str | None


class GuestOut(ORMModel):
    """An invitation flattened with its person, host and event."""

    id: IdStr
    person_id: IdStr
    host_id: IdStr
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

    allocated_tennis_session: str | None
    workshop: str | None
    additional_experience: str | None
    sightseeing_contact_email: str | None
    additional_information: str | None

    person: PersonOut
    host: HostOut
    event: EventOut

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        parts = [self.person.first_name, self.person.last_name]
        return " ".join(p for p in parts if p) or "(unnamed)"
