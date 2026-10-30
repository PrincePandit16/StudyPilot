from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.studypilot.core.database import get_db
from src.studypilot.core.dependencies import get_current_user
from src.studypilot.services.user_service import UserService
from src.studypilot.schemas.user import UserUpdate, UserResponse
from src.studypilot.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    return service.update_user_profile(current_user.id, user_update)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    if not service.delete_user_account(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
