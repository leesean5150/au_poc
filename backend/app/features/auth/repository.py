from sqlalchemy.orm import Session

from app.core.models import User
from app.core.security import roles_for


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def roles_for(self, user_id: int) -> list[str]:
        return roles_for(self.db, user_id)
