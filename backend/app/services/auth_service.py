from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    # Case-insensitive match so "A@b.com" and "a@b.com" are the same account.
    result = await db.execute(
        select(User).where(func.lower(User.email) == email.lower())
    )
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, email: str, password: str, name: str) -> User:
    """Create a new user. Raises ValueError if the email is already taken."""
    existing = await get_user_by_email(db, email)
    if existing is not None:
        raise ValueError("An account with this email already exists")

    user = User(
        email=email.lower(),
        name=name or "",
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
