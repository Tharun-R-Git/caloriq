from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserProfileResponse
from app.services import auth_service
from app.services.profile_service import build_profile_response

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register_user(db, data.email, data.password, data.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    token = create_access_token(user.id)
    return {"access_token": token, "user": build_profile_response(user)}


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(user.id)
    return {"access_token": token, "user": build_profile_response(user)}


@router.get("/me", response_model=UserProfileResponse)
async def me(user: User = Depends(get_current_user)):
    return build_profile_response(user)
