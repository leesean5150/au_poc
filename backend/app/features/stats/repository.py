from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.models import Event, Invitation
from app.core.scoping import default_event_id


class StatsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def event(self, event_id: int | None) -> Event | None:
        if event_id is not None:
            return self.db.get(Event, event_id)
        resolved = default_event_id(self.db)
        return self.db.get(Event, resolved) if resolved is not None else None

    def invitations_for_event(self, event_id: int) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .where(Invitation.event_id == event_id)
            .options(
                selectinload(Invitation.person),
                selectinload(Invitation.host),
            )
        )
        return list(self.db.scalars(stmt))

    def all_events(self) -> list[Event]:
        return list(self.db.scalars(select(Event).order_by(Event.starts_on.asc())))
