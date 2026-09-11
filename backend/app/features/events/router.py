from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.schemas import EventOut
from app.features.events.repository import EventRepository
from app.features.events.service import EventService

router = APIRouter(prefix="/api/events", tags=["events"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> EventService:
    return EventService(EventRepository(db))


@router.get("", response_model=list[EventOut])
def list_events(service: Annotated[EventService, Depends(get_service)]) -> list[EventOut]:
    return service.list_events()
