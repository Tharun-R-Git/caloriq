from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


async def get_or_create_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        user = User()
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@router.get("", response_model=UserRead)
async def get_profile(db: AsyncSession = Depends(get_db)):
    return await get_or_create_user(db)


@router.put("", response_model=UserRead)
async def update_profile(data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await get_or_create_user(db)
    for k, v in data.model_dump().items():
        setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user
