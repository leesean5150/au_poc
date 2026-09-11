"""Idempotent seed: import the bundled xlsx when the DB has no invitations,
then mock a few standalone future events (with a handful of guests re-invited)
so the dashboard's upcoming-events box and cross-event history have content.
"""

from __future__ import annotations

import sys
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.db import SessionLocal
from app.core.models import Event, Host, Invitation, Person
from app.features.imports.importer import import_workbook

# Standalone events, all dated after APP_NOW (2026-01-05) so they surface as
# "upcoming". No hierarchy — every event is first-class.
EXTRA_EVENTS = [
    {
        "name": "Sydney Broker Roadshow",
        "event_type": "conference",
        "starts_on": date(2026, 2, 24),
        "ends_on": date(2026, 2, 25),
        "location": "Sydney",
    },
    {
        "name": "Brisbane Client Golf Day",
        "event_type": "experience",
        "starts_on": date(2026, 3, 19),
        "ends_on": None,
        "location": "Brisbane",
    },
    {
        "name": "Perth Partner Dinner",
        "event_type": "dinner",
        "starts_on": date(2026, 5, 7),
        "ends_on": None,
        "location": "Perth",
    },
]

# event name -> [(person_index, host_index)] into the id-ordered people / hosts.
# Overlaps across events on purpose, so some people gain a real invite history.
EXTRA_INVITES: dict[str, list[tuple[int, int]]] = {
    "Sydney Broker Roadshow": [(0, 0), (1, 1), (2, 2), (3, 3), (4, 0), (5, 1), (6, 2), (7, 3)],
    "Brisbane Client Golf Day": [(4, 4), (5, 5), (6, 6), (8, 7), (10, 8)],
    "Perth Partner Dinner": [(1, 0), (3, 2), (5, 4), (7, 6)],
}

_STATUSES = ["accepted", "invite_sent", "to_send_invite", "waiting_for_information"]


def seed(*, force: bool = False) -> None:
    settings = get_settings()
    with SessionLocal() as db:
        existing = db.scalar(select(func.count()).select_from(Invitation)) or 0
        if existing and not force:
            print(f"[seed] {existing} invitations present — skipping")
            return
        result = import_workbook(db, settings.data_file)
        _seed_extra_events(db)
        db.commit()
        print(f"[seed] {result}")


def _seed_extra_events(db: Session) -> None:
    people = list(db.scalars(select(Person).order_by(Person.id)))
    hosts = list(db.scalars(select(Host).order_by(Host.id)))
    if not people or not hosts:
        return

    for spec in EXTRA_EVENTS:
        event = db.scalar(select(Event).where(Event.name == spec["name"]))
        if event is None:
            event = Event(**spec)
            db.add(event)
            db.flush()

        for n, (person_idx, host_idx) in enumerate(EXTRA_INVITES[spec["name"]]):
            person = people[person_idx % len(people)]
            host = hosts[host_idx % len(hosts)]
            already = db.scalar(
                select(Invitation).where(
                    Invitation.person_id == person.id,
                    Invitation.event_id == event.id,
                )
            )
            if already is not None:
                continue
            db.add(
                Invitation(
                    person=person,
                    host=host,
                    event=event,
                    registration_type="A-Generic",
                    status=_STATUSES[n % len(_STATUSES)],
                    compliance_approved={0: True, 1: False}.get(n % 3),
                    requires_flights=True,
                    flight_class="economy",
                    requires_accommodation=True,
                    requires_airport_transfer=(n % 2 == 0),
                )
            )


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
