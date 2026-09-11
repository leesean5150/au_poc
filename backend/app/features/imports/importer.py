"""xlsx -> DB rows. Single source of truth for the spreadsheet mapping.

Upsert order: event -> people -> hosts -> invitations.
People dedupe on lowercased ``work_email``; hosts on lowercased ``email``.
Unknown categorical values round-trip rather than raising.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import BinaryIO

from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Event, Host, Invitation, Person

SHEET_NAME = "Aus Guest List"

DEFAULT_EVENT: dict[str, object] = {
    "name": "Melbourne Hospitality Event",
    "starts_on": date(2026, 1, 18),
    "ends_on": date(2026, 1, 20),
    "location": "Melbourne",
}

# --- spreadsheet column -> model field ---------------------------------------
PERSON_COLUMNS = {
    "Title": "title",
    "Guest First Name": "first_name",
    "Guest Last Name": "last_name",
    "Work Email": "work_email",
    "Company": "company",
    "Job Title": "job_title",
    "Guest City of Residence": "city_of_residence",
}
HOST_COLUMNS = {
    "Host First Name": "first_name",
    "Host Last Name": "last_name",
    "Host Email Address": "email",
    "Host's City of Residence": "city_of_residence",
    "Department": "department",
}
# plain free-text / string invitation fields
INVITATION_TEXT_COLUMNS = {
    "Registration Type": "registration_type",
    "Group Name": "group_name",
    "Business Case for Invite": "business_case",
    "Departure City": "departure_city",
    "Allocated Tennis Session": "allocated_tennis_session",
    "Workshop/Conference": "workshop",
    "Additional Experience": "additional_experience",
    "Email of Internal Contact Who Will manage Sightseeing Activity": (
        "sightseeing_contact_email"
    ),
    "Additional Information": "additional_information",
}
COL_STATUS = "Status"
COL_COMPLIANCE = "Compliance Approve (yes/no)"
COL_GUEST_TYPE = "Broker/Client/Affinity Partner/Staff/Other"
COL_FLIGHTS = "Will Guest Require Flights to Melbourne"
COL_FLIGHT_CLASS = "if yes, what flight class does this guest require?"
COL_TRANSFER = "Does Guest Require Airport Transfer?"
COL_TRANSFER_TYPE = (
    "Can Your Guest Travel In a Group Transfer From The Airport To Hotel? "
    "Is Private Transfer Needed?"
)
COL_ACCOMMODATION = "Will Your Guest Require Accomodation in Melbourne?"
COL_CHECK_IN = "Check In Date"
COL_CHECK_OUT = "Check Out Date"

STATUS_MAP = {
    "waiting for information": "waiting_for_information",
    "to send invite": "to_send_invite",
    "invite": "invite_sent",
    "invite sent": "invite_sent",
    "accepted": "accepted",
    "declined": "declined",
}
GUEST_TYPE_MAP = {
    "broker": "broker",
    "client": "client",
    "affinity partner": "affinity_partner",
    "staff": "staff",
    "other": "other",
}
FLIGHT_CLASS_MAP = {"economy": "economy", "business": "business", "first": "first"}
TRANSFER_TYPE_MAP = {
    "group transfer": "group",
    "private transfer": "private",
    "individual transfer": "individual",
}


# --- normalizers -----------------------------------------------------------
def _text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        value = value.date()
    s = str(value).strip()
    return s or None


def _key(value: object) -> str | None:
    s = _text(value)
    return s.lower() if s else None


def _bool(value: object) -> bool | None:
    k = _key(value)
    if k in {"yes", "y", "true"}:
        return True
    if k in {"no", "n", "false"}:
        return False
    return None


def _date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = _text(value)
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def _na(value: object) -> str | None:
    """Free-text value with the literal 'N/A' collapsed to None."""
    s = _text(value)
    if s is None or s.strip().lower() in {"n/a", "na"}:
        return None
    return s


@dataclass
class ImportResult:
    people_created: int = 0
    people_updated: int = 0
    hosts_created: int = 0
    invitations_created: int = 0
    invitations_updated: int = 0
    skipped: int = 0


def import_workbook(
    db: Session,
    source: str | BinaryIO,
    *,
    event_name: str | None = None,
    event_starts_on: date | None = None,
    event_ends_on: date | None = None,
) -> ImportResult:
    wb = load_workbook(source, read_only=True, data_only=True)
    ws = wb[SHEET_NAME] if SHEET_NAME in wb.sheetnames else wb[wb.sheetnames[0]]

    rows = ws.iter_rows(values_only=True)
    header = [(_text(cell) or "") for cell in next(rows)]

    result = ImportResult()
    people: dict[str, Person] = {}
    hosts: dict[str, Host] = {}

    event = _upsert_event(db, event_name, event_starts_on, event_ends_on)
    db.flush()

    for raw in rows:
        record = dict(zip(header, raw, strict=False))
        if _key(record.get("Work Email")) is None:
            result.skipped += 1
            continue

        person = _upsert_person(db, record, people, result)
        host = _upsert_host(db, record, hosts, result)
        db.flush()
        _upsert_invitation(db, record, person, host, event, result)

    db.commit()
    return result


def _upsert_event(
    db: Session,
    name: str | None,
    starts_on: date | None,
    ends_on: date | None,
) -> Event:
    name = (name or "").strip() or str(DEFAULT_EVENT["name"])
    event = db.scalar(select(Event).where(Event.name == name))
    if event is None:
        event = Event(
            name=name,
            event_type="main",
            starts_on=starts_on or DEFAULT_EVENT["starts_on"],
            ends_on=ends_on or DEFAULT_EVENT["ends_on"],
            location=str(DEFAULT_EVENT["location"]),
        )
        db.add(event)
    else:
        if starts_on:
            event.starts_on = starts_on
        if ends_on:
            event.ends_on = ends_on
    return event


def _upsert_person(
    db: Session, record: dict, cache: dict[str, Person], result: ImportResult
) -> Person:
    email = _key(record.get("Work Email"))
    assert email is not None  # guarded by caller

    fields = {dst: _text(record.get(src)) for src, dst in PERSON_COLUMNS.items()}
    fields["work_email"] = email
    fields["guest_type"] = GUEST_TYPE_MAP.get(
        _key(record.get(COL_GUEST_TYPE)) or "", _key(record.get(COL_GUEST_TYPE)) or "other"
    )

    person = cache.get(email) or db.scalar(
        select(Person).where(Person.work_email == email)
    )
    if person is None:
        person = Person(**fields)
        db.add(person)
        result.people_created += 1
    else:
        for key, value in fields.items():
            setattr(person, key, value)
        result.people_updated += 1
    cache[email] = person
    return person


def _upsert_host(
    db: Session, record: dict, cache: dict[str, Host], result: ImportResult
) -> Host:
    email = _key(record.get("Host Email Address"))
    fields = {dst: _text(record.get(src)) for src, dst in HOST_COLUMNS.items()}
    fields["email"] = email

    lookup_key = email or f"__noemail__{fields.get('first_name')}_{fields.get('last_name')}"
    host = cache.get(lookup_key)
    if host is None and email:
        host = db.scalar(select(Host).where(Host.email == email))
    if host is None:
        host = Host(**fields)
        db.add(host)
        result.hosts_created += 1
    else:
        for key, value in fields.items():
            setattr(host, key, value)
    cache[lookup_key] = host
    return host


def _upsert_invitation(
    db: Session,
    record: dict,
    person: Person,
    host: Host,
    event: Event,
    result: ImportResult,
) -> Invitation:
    fields: dict[str, object] = {
        dst: _na(record.get(src)) for src, dst in INVITATION_TEXT_COLUMNS.items()
    }
    fields.update(
        status=STATUS_MAP.get(
            _key(record.get(COL_STATUS)) or "", _key(record.get(COL_STATUS)) or "waiting_for_information"
        ),
        compliance_approved=_bool(record.get(COL_COMPLIANCE)),
        requires_flights=_bool(record.get(COL_FLIGHTS)),
        flight_class=FLIGHT_CLASS_MAP.get(_key(record.get(COL_FLIGHT_CLASS)) or ""),
        requires_airport_transfer=_bool(record.get(COL_TRANSFER)),
        transfer_type=TRANSFER_TYPE_MAP.get(_key(record.get(COL_TRANSFER_TYPE)) or ""),
        requires_accommodation=_bool(record.get(COL_ACCOMMODATION)),
        check_in_date=_date(record.get(COL_CHECK_IN)),
        check_out_date=_date(record.get(COL_CHECK_OUT)),
    )

    invitation = None
    if person.id is not None:
        invitation = db.scalar(
            select(Invitation).where(
                Invitation.person_id == person.id,
                Invitation.event_id == event.id,
            )
        )
    if invitation is None:
        invitation = Invitation(person=person, host=host, event=event, **fields)
        db.add(invitation)
        result.invitations_created += 1
    else:
        invitation.host = host
        for key, value in fields.items():
            setattr(invitation, key, value)
        result.invitations_updated += 1
    return invitation
