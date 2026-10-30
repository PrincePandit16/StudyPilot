from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.studypilot.repositories.user_repository import UserRepository
from src.studypilot.schemas.user import UserCreate, UserResponse
from src.studypilot.core.auth_utils import AuthUtils

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register_user(self, user_in: UserCreate) -> UserResponse:
        if self.repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user = self.repo.create(user_in)
        return UserResponse.model_validate(user)

    def authenticate_user(self, email: str, password: str) -> UserResponse:
        user = self.repo.get_by_email(email)
        if not user or not AuthUtils.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        return UserResponse.model_validate(user)

    def get_user_profile(self, user_id: UUID) -> UserResponse:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_validate(user)

    def update_user_profile(self, user_id: UUID, user_in: UserUpdate) -> UserResponse:
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = AuthUtils.get_password_hash(update_data.pop("password"))

        user = self.repo.update(user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_validate(user)

    def delete_user_account(self, user_id: UUID) -> bool:
        return self.repo.delete(user_id)
