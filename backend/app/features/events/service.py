from app.core.schemas import EventOut
from app.features.events.repository import EventRepository


class EventService:
    def __init__(self, repo: EventRepository) -> None:
        self.repo = repo

    def list_events(self) -> list[EventOut]:
        return [EventOut.model_validate(e) for e in self.repo.list_ordered()]
