from pydantic import BaseModel

from app.core.schemas import IdStr


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: IdStr
    email: str
    first_name: str | None
    last_name: str | None
    roles: list[str]
