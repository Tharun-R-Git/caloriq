import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


def _normalize_db_url(url: str) -> str:
    """Render hands out 'postgres://...' URLs; SQLAlchemy's async engine needs
    the 'postgresql+asyncpg://' driver prefix. Rewrite so the same env var works
    in production (Postgres) and locally (SQLite default)."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


DATABASE_URL = _normalize_db_url(os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./caloriq.db"))

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def _add_column(table: str, col: str, typedef: str) -> None:
    """Add a column if it doesn't already exist, each in its own transaction.

    SQLite has no 'ADD COLUMN IF NOT EXISTS', so we try/except. Postgres *does*,
    and — unlike SQLite — a failed statement poisons the surrounding transaction,
    so each ALTER must run in its own transaction block."""
    is_pg = engine.dialect.name == "postgresql"
    if is_pg:
        sql = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {typedef}"
    else:
        sql = f"ALTER TABLE {table} ADD COLUMN {col} {typedef}"
    try:
        async with engine.begin() as conn:
            await conn.execute(text(sql))
    except Exception:
        pass


async def init_db():
    from app.models import user, food_entry, exercise_entry  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Lightweight migrations for columns added after the original schema.
    food_cols = [
        ("user_id", "INTEGER DEFAULT 1"),
        ("description", "TEXT"),
        ("protein_g", "REAL DEFAULT 0"),
        ("carbs_g", "REAL DEFAULT 0"),
        ("fat_g", "REAL DEFAULT 0"),
        ("serving_size", "TEXT"),
        ("logged_at", "TIMESTAMP"),
    ]
    for col, typedef in food_cols:
        await _add_column("food_entries", col, typedef)

    exercise_cols = [
        ("user_id", "INTEGER DEFAULT 1"),
        ("intensity", "TEXT DEFAULT 'moderate'"),
        ("logged_at", "TIMESTAMP"),
    ]
    for col, typedef in exercise_cols:
        await _add_column("exercise_entries", col, typedef)

    user_cols = [
        ("email", "TEXT"),
        ("password_hash", "TEXT"),
        ("gender", "TEXT"),
        ("aim", "TEXT"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("dietary_preference", "TEXT"),
        ("cuisine_preferences", "TEXT"),
    ]
    for col, typedef in user_cols:
        await _add_column("users", col, typedef)


async def get_db():
    async with SessionLocal() as session:
        yield session
