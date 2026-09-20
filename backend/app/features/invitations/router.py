from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.pagination import Page, PageParams, page_params
from app.features.invitations.repository import InvitationRepository
from app.features.invitations.schemas import InvitationFilters, InvitationOut, InvitationPatch
from app.features.invitations.service import InvitationService

router = APIRouter(prefix="/api/invitations", tags=["invitations"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> InvitationService:
    return InvitationService(InvitationRepository(db))


ServiceDep: TypeAlias = Annotated[InvitationService, Depends(get_service)]


@router.get("", response_model=Page[InvitationOut])
def list_invitations(
    service: ServiceDep,
    filters: Annotated[InvitationFilters, Query()],
    page: Annotated[PageParams, Depends(page_params)],
) -> Page[InvitationOut]:
    return service.list_invitations(filters, page)


@router.get("/{invitation_id}", response_model=InvitationOut)
def get_invitation(service: ServiceDep, invitation_id: int) -> InvitationOut:
    return service.get_invitation(invitation_id)


@router.patch("/{invitation_id}", response_model=InvitationOut)
def patch_invitation(
    service: ServiceDep, invitation_id: int, patch: InvitationPatch
) -> InvitationOut:
    return service.update_invitation(invitation_id, patch)
