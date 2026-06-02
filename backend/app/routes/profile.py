from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.user import ProfileSetup, UserUpdate, UserProfileResponse, GoalsResponse
from app.services.calorie_engine import calculate_daily_goal
from app.services.profile_service import get_or_create_user, build_profile_response, list_to_cuisine

router = APIRouter()


@router.get("", response_model=UserProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    user = await get_or_create_user(db)
    return build_profile_response(user)


@router.post("/setup", response_model=UserProfileResponse)
async def setup_profile(data: ProfileSetup, db: AsyncSession = Depends(get_db)):
    user = await get_or_create_user(db)
    payload = data.model_dump()
    cuisine_list = payload.pop("cuisine_preferences", None)
    for k, v in payload.items():
        setattr(user, k, v)
    user.cuisine_preferences = list_to_cuisine(cuisine_list)
    user.goal_calories = calculate_daily_goal(user)["daily_goal"]
    await db.commit()
    await db.refresh(user)
    return build_profile_response(user)


@router.get("/goals", response_model=GoalsResponse)
async def get_goals(db: AsyncSession = Depends(get_db)):
    user = await get_or_create_user(db)
    return calculate_daily_goal(user)


@router.put("", response_model=UserProfileResponse)
async def update_profile(data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await get_or_create_user(db)
    payload = data.model_dump(exclude_none=True)
    cuisine_list = payload.pop("cuisine_preferences", None)
    for k, v in payload.items():
        setattr(user, k, v)
    if cuisine_list is not None:
        user.cuisine_preferences = list_to_cuisine(cuisine_list)
    user.goal_calories = calculate_daily_goal(user)["daily_goal"]
    await db.commit()
    await db.refresh(user)
    return build_profile_response(user)
