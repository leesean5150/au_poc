from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.models import User
from app.core.security import get_current_user
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import LoginRequest, MeOut, TokenOut
from app.features.auth.service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(AuthRepository(db))


ServiceDep: TypeAlias = Annotated[AuthService, Depends(get_service)]


@router.post("/login", response_model=TokenOut)
def login(service: ServiceDep, credentials: LoginRequest) -> TokenOut:
    return service.login(credentials)


@router.get("/me", response_model=MeOut)
def me(
    service: ServiceDep,
    user: Annotated[User, Depends(get_current_user)],
) -> MeOut:
    return service.me(user)
