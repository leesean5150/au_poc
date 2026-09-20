"""xlsx -> DB rows. Single source of truth for the spreadsheet mapping.

Upsert order: users/guest_profiles -> users/host_profiles -> event ->
invitations, per row (each row's event is derived from its own "Allocated
Tennis Session" label). Guests and hosts dedupe on lowercased email against
the shared ``users`` table. Unknown categorical values round-trip rather
than raising.

This importer is a legacy porting tool for the source spreadsheet's free-text
session label and is allowed to be fragile about that one column: if any
row's label can't be parsed into a date, the whole import raises
``SessionParseError`` and nothing is committed (see ``import_workbook`` — the
raise happens before the trailing ``db.commit()``, so the caller's session
rolls back the entire batch rather than importing a partial file).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import BinaryIO

from dateutil import parser as dateutil_parser
from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Event, GuestProfile, HostProfile, Invitation, User

SHEET_NAME = "Aus Guest List"
COL_SESSION = "Allocated Tennis Session"


class SessionParseError(ValueError):
    """Raised when a row's Allocated Tennis Session label has no parseable date."""


# --- spreadsheet column -> model field ---------------------------------------
GUEST_USER_COLUMNS = {
    "Guest First Name": "first_name",
    "Guest Last Name": "last_name",
}
GUEST_PROFILE_COLUMNS = {
    "Title": "title",
    "Company": "company",
    "Job Title": "job_title",
    "Guest City of Residence": "city_of_residence",
}
HOST_USER_COLUMNS = {
    "Host First Name": "first_name",
    "Host Last Name": "last_name",
}
HOST_PROFILE_COLUMNS = {
    "Host's City of Residence": "city_of_residence",
    "Department": "department",
}
# plain free-text / string invitation fields
INVITATION_TEXT_COLUMNS = {
    "Registration Type": "registration_type",
    "Group Name": "group_name",
    "Business Case for Invite": "business_case",
    "Departure City": "departure_city",
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


def import_workbook(db: Session, source: str | BinaryIO) -> ImportResult:
    wb = load_workbook(source, read_only=True, data_only=True)
    ws = wb[SHEET_NAME] if SHEET_NAME in wb.sheetnames else wb[wb.sheetnames[0]]

    rows = ws.iter_rows(values_only=True)
    header = [(_text(cell) or "") for cell in next(rows)]

    result = ImportResult()
    guests: dict[str, GuestProfile] = {}
    hosts: dict[str, HostProfile] = {}
    events: dict[str, Event] = {}

    for raw in rows:
        record = dict(zip(header, raw, strict=False))
        if _key(record.get("Work Email")) is None:
            result.skipped += 1
            continue

        # Fragile by design (legacy porting tool) — but an unparseable label
        # aborts the whole import rather than silently skipping/mis-filing
        # a row, so nothing is committed on a partial failure.
        session_name, session_date = _parse_session(record.get(COL_SESSION))

        guest = _upsert_guest(db, record, guests, result)
        host = _upsert_host(db, record, hosts, result)
        event = _upsert_event(db, events, session_name, session_date)
        db.flush()
        _upsert_invitation(db, record, guest, host, event, result)

    db.commit()
    return result


def _parse_session(label: object) -> tuple[str, date]:
    """A row's raw "Allocated Tennis Session" text is used verbatim as the
    Event.name (e.g. "Monday 19 Jan Day Session") and fuzzy-parsed for its
    date. Raises SessionParseError if the label is blank or has no
    recognizable date — the caller must not catch this per-row; it's meant
    to fail the whole import.
    """
    name = _text(label)
    if name is None:
        raise SessionParseError("row has no Allocated Tennis Session label")
    try:
        parsed = dateutil_parser.parse(name, fuzzy=True)
    except (ValueError, OverflowError) as exc:
        raise SessionParseError(
            f"could not parse a date out of Allocated Tennis Session {name!r}"
        ) from exc
    return name, parsed.date()


def _upsert_event(
    db: Session, cache: dict[str, Event], name: str, starts_on: date
) -> Event:
    event = cache.get(name)
    if event is None:
        event = db.scalar(select(Event).where(Event.name == name))
        if event is None:
            event = Event(name=name, starts_on=starts_on, location="Melbourne")
            db.add(event)
            db.flush()
        cache[name] = event
    return event


def _upsert_user(db: Session, email: str, fields: dict) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, password_hash=None, status="active", **fields)
        db.add(user)
        db.flush()
    else:
        for key, value in fields.items():
            setattr(user, key, value)
    return user


def _upsert_guest(
    db: Session, record: dict, cache: dict[str, GuestProfile], result: ImportResult
) -> GuestProfile:
    email = _key(record.get("Work Email"))
    assert email is not None  # guarded by caller

    user_fields = {dst: _text(record.get(src)) for src, dst in GUEST_USER_COLUMNS.items()}
    profile_fields = {
        dst: _text(record.get(src)) for src, dst in GUEST_PROFILE_COLUMNS.items()
    }
    profile_fields["guest_type"] = GUEST_TYPE_MAP.get(
        _key(record.get(COL_GUEST_TYPE)) or "", _key(record.get(COL_GUEST_TYPE)) or "other"
    )

    guest = cache.get(email)
    if guest is None:
        user = _upsert_user(db, email, user_fields)
        guest = db.get(GuestProfile, user.id)
        if guest is None:
            guest = GuestProfile(user_id=user.id, **profile_fields)
            db.add(guest)
            result.people_created += 1
        else:
            for key, value in profile_fields.items():
                setattr(guest, key, value)
            result.people_updated += 1
    else:
        for key, value in user_fields.items():
            setattr(guest.user, key, value)
        for key, value in profile_fields.items():
            setattr(guest, key, value)
        result.people_updated += 1
    cache[email] = guest
    return guest


def _upsert_host(
    db: Session, record: dict, cache: dict[str, HostProfile], result: ImportResult
) -> HostProfile:
    email = _key(record.get("Host Email Address"))
    user_fields = {dst: _text(record.get(src)) for src, dst in HOST_USER_COLUMNS.items()}
    profile_fields = {
        dst: _text(record.get(src)) for src, dst in HOST_PROFILE_COLUMNS.items()
    }

    lookup_key = email or f"__noemail__{user_fields.get('first_name')}_{user_fields.get('last_name')}"
    host = cache.get(lookup_key)
    if host is None:
        # No email to dedupe on across runs — still needs a users row.
        lookup_email = email or (
            f"__no-email__{user_fields.get('first_name')}."
            f"{user_fields.get('last_name')}@unknown.local"
        ).lower()
        user = _upsert_user(db, lookup_email, user_fields)
        host = db.get(HostProfile, user.id)
        if host is None:
            host = HostProfile(user_id=user.id, **profile_fields)
            db.add(host)
            result.hosts_created += 1
        else:
            for key, value in profile_fields.items():
                setattr(host, key, value)
    else:
        for key, value in user_fields.items():
            setattr(host.user, key, value)
        for key, value in profile_fields.items():
            setattr(host, key, value)
    cache[lookup_key] = host
    return host


def _upsert_invitation(
    db: Session,
    record: dict,
    guest: GuestProfile,
    host: HostProfile,
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
    if guest.user_id is not None:
        invitation = db.scalar(
            select(Invitation).where(
                Invitation.guest_user_id == guest.user_id,
                Invitation.event_id == event.id,
            )
        )
    if invitation is None:
        invitation = Invitation(guest=guest, host=host, event=event, **fields)
        db.add(invitation)
        result.invitations_created += 1
    else:
        invitation.host = host
        for key, value in fields.items():
            setattr(invitation, key, value)
        result.invitations_updated += 1
    return invitation
