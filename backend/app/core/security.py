from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.db import get_db
from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.models import Permission, RolePermission, Role, User, UserRole

_JWT_ALGORITHM = "HS256"

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user: User, roles: list[str]) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expires_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("invalid or expired token") from exc


def get_current_user(
    token: Annotated[str | None, Depends(_oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if token is None:
        raise UnauthorizedError("not authenticated")
    payload = decode_access_token(token)
    user = db.get(User, int(payload["sub"]))
    if user is None or user.status != "active":
        raise UnauthorizedError("invalid or expired token")
    return user


def roles_for(db: Session, user_id: int) -> list[str]:
    stmt = (
        select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(
            UserRole.user_id == user_id
        )
    )
    return list(db.scalars(stmt))


def require_roles(*names: str) -> Callable[..., User]:
    def _check(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> User:
        if not set(roles_for(db, user.id)) & set(names):
            raise ForbiddenError("insufficient role")
        return user

    return _check


def require_permission(key: str) -> Callable[..., User]:
    def _check(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> User:
        stmt = (
            select(Permission.key)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user.id, Permission.key == key)
        )
        if db.scalar(stmt) is None:
            raise ForbiddenError("insufficient permission")
        return user

    return _check
