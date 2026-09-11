from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Event


class EventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_ordered(self) -> list[Event]:
        stmt = select(Event).order_by(Event.starts_on.asc(), Event.id.asc())
        return list(self.db.scalars(stmt))
