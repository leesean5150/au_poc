from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.pagination import Page, PageParams, page_params
from app.core.schemas import PersonOut
from app.features.people.repository import PeopleRepository
from app.features.people.schemas import (
    PersonDetail,
    PersonFilters,
    PersonPatch,
    PersonRow,
)
from app.features.people.service import PeopleService

router = APIRouter(prefix="/api/people", tags=["people"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> PeopleService:
    return PeopleService(PeopleRepository(db))


ServiceDep: TypeAlias = Annotated[PeopleService, Depends(get_service)]


@router.get("", response_model=Page[PersonRow])
def list_people(
    service: ServiceDep,
    filters: Annotated[PersonFilters, Query()],
    page: Annotated[PageParams, Depends(page_params)],
) -> Page[PersonRow]:
    return service.list_people(filters, page)


@router.get("/{person_id}", response_model=PersonDetail)
def get_person(service: ServiceDep, person_id: int) -> PersonDetail:
    return service.get_person(person_id)


@router.patch("/{person_id}", response_model=PersonOut)
def patch_person(
    service: ServiceDep, person_id: int, patch: PersonPatch
) -> PersonOut:
    return service.update_person(person_id, patch)
