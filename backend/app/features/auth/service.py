from app.core.errors import UnauthorizedError
from app.core.models import User
from app.core.security import create_access_token, verify_password
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import LoginRequest, MeOut, TokenOut


class AuthService:
    def __init__(self, repo: AuthRepository) -> None:
        self.repo = repo

    def login(self, credentials: LoginRequest) -> TokenOut:
        user = self.repo.get_by_email(credentials.email.lower())
        if (
            user is None
            or user.password_hash is None
            or user.status != "active"
            or not verify_password(credentials.password, user.password_hash)
        ):
            raise UnauthorizedError("invalid email or password")

        roles = self.repo.roles_for(user.id)
        token = create_access_token(user, roles)
        return TokenOut(access_token=token)

    def me(self, user: User) -> MeOut:
        roles = self.repo.roles_for(user.id)
        return MeOut(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=roles,
        )
