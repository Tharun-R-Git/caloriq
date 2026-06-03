import pytest
import pytest_asyncio
from fastapi import Depends
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db import get_db, Base
from app.dependencies import get_current_user
from app.models.user import User

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DB_URL)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


async def override_get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    # Resolve through the request's own session (Depends(get_db) is cached per
    # request) so the returned user is attached to the session routes mutate.
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(email="test@example.com", name="Test User")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Authenticated client — auth is bypassed with a fixed test user so the
    existing feature tests don't each need to register/login."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def raw_client():
    """Client with real JWT auth (no get_current_user override) for auth tests."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
