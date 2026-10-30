from sqlalchemy.orm import Session
from sqlalchemy import select
from src.studypilot.models.user import User
from src.studypilot.schemas.user import UserCreate
from src.studypilot.core.auth_utils import AuthUtils

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    def create(self, user_data: UserCreate) -> User:
        hashed_password = AuthUtils.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
