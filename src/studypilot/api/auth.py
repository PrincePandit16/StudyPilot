from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.studypilot.core.database import get_db
from src.studypilot.core.auth_utils import AuthUtils
from src.studypilot.services.user_service import UserService
from src.studypilot.schemas.user import UserCreate, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.register_user(user_in)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.authenticate_user(form_data.username, form_data.password)

    access_token = AuthUtils.create_access_token(
        data={"sub": str(user.id)}
    )
    return Token(access_token=access_token, token_type="bearer")
