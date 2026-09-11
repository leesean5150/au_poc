from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.features.imports.schemas import ImportResultOut
from app.features.imports.service import ImportService

router = APIRouter(prefix="/api", tags=["imports"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> ImportService:
    return ImportService(db)


@router.post("/import", response_model=ImportResultOut)
async def import_xlsx(
    service: Annotated[ImportService, Depends(get_service)],
    file: Annotated[UploadFile, File()],
    event_name: Annotated[str | None, Form()] = None,
    event_starts_on: Annotated[date | None, Form()] = None,
    event_ends_on: Annotated[date | None, Form()] = None,
) -> ImportResultOut:
    data = await file.read()
    return service.import_bytes(
        data,
        event_name=event_name,
        event_starts_on=event_starts_on,
        event_ends_on=event_ends_on,
    )
