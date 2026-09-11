from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.pagination import Page, PageParams, page_params
from app.features.hosts.repository import HostRepository
from app.features.hosts.schemas import HostDetail, HostFilters, HostRow
from app.features.hosts.service import HostService

router = APIRouter(prefix="/api/hosts", tags=["hosts"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> HostService:
    return HostService(HostRepository(db))


ServiceDep: TypeAlias = Annotated[HostService, Depends(get_service)]


@router.get("", response_model=Page[HostRow])
def list_hosts(
    service: ServiceDep,
    filters: Annotated[HostFilters, Query()],
    page: Annotated[PageParams, Depends(page_params)],
) -> Page[HostRow]:
    return service.list_hosts(filters, page)


@router.get("/{host_id}", response_model=HostDetail)
def get_host(
    service: ServiceDep,
    host_id: int,
    event_id: Annotated[int | None, Query()] = None,
) -> HostDetail:
    return service.get_host(host_id, event_id)
