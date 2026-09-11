from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.pagination import Page, PageParams, page_params
from app.features.guests.repository import GuestRepository
from app.features.guests.schemas import GuestFilters, GuestOut, GuestPatch
from app.features.guests.service import GuestService

router = APIRouter(prefix="/api/guests", tags=["guests"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> GuestService:
    return GuestService(GuestRepository(db))


ServiceDep: TypeAlias = Annotated[GuestService, Depends(get_service)]


@router.get("", response_model=Page[GuestOut])
def list_guests(
    service: ServiceDep,
    filters: Annotated[GuestFilters, Query()],
    page: Annotated[PageParams, Depends(page_params)],
) -> Page[GuestOut]:
    return service.list_guests(filters, page)


@router.get("/{invitation_id}", response_model=GuestOut)
def get_guest(service: ServiceDep, invitation_id: int) -> GuestOut:
    return service.get_guest(invitation_id)


@router.patch("/{invitation_id}", response_model=GuestOut)
def patch_guest(
    service: ServiceDep, invitation_id: int, patch: GuestPatch
) -> GuestOut:
    return service.update_guest(invitation_id, patch)
