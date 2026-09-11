from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.stats.repository import StatsRepository
from app.features.stats.schemas import StatsOverview
from app.features.stats.service import StatsService

router = APIRouter(prefix="/api/stats", tags=["stats"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> StatsService:
    return StatsService(StatsRepository(db))


@router.get("/overview", response_model=StatsOverview)
def overview(
    service: Annotated[StatsService, Depends(get_service)],
    event_id: Annotated[int | None, Query()] = None,
) -> StatsOverview:
    return service.overview(event_id)
