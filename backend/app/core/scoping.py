from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Event


def default_event_id(db: Session) -> int | None:
    """The event that list / stats endpoints scope to when the request omits
    ``event_id``. Every event is first-class and equal — there is no privileged
    type — so this is just the earliest one (ties broken by id)."""
    return db.scalar(
        select(Event.id).order_by(Event.starts_on.asc(), Event.id.asc()).limit(1)
    )
