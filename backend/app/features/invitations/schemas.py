from datetime import date

from pydantic import BaseModel, ConfigDict

from app.core.schemas import InvitationOut

__all__ = ["InvitationOut", "InvitationPatch", "InvitationFilters"]


class InvitationPatch(BaseModel):
    """Editable invitation fields. Identity fields live on PATCH /api/people."""

    model_config = ConfigDict(extra="forbid")

    registration_type: str | None = None
    group_name: str | None = None
    business_case: str | None = None
    compliance_approved: bool | None = None
    status: str | None = None
    requires_flights: bool | None = None
    flight_class: str | None = None
    departure_city: str | None = None
    requires_airport_transfer: bool | None = None
    transfer_type: str | None = None
    requires_accommodation: bool | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    workshop: str | None = None
    additional_experience: str | None = None
    sightseeing_contact_email: str | None = None
    additional_information: str | None = None


class InvitationFilters(BaseModel):
    event_id: int | None = None
    status: str | None = None
    guest_type: str | None = None
    registration_type: str | None = None
    department: str | None = None
    host_user_id: int | None = None
    guest_user_id: int | None = None
    compliance_approved: str | None = None  # "yes" | "no" | "pending"
    search: str | None = None
    sort: str = "name"
    order: str = "asc"
