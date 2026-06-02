import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./caloriq.db")

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        from app.models import user, food_entry, exercise_entry  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

        # Add new columns to food_entries that may be missing from an older schema.
        # try/except is intentional: SQLite raises if the column already exists.
        new_cols = [
            ("user_id", "INTEGER DEFAULT 1"),
            ("description", "TEXT"),
            ("protein_g", "REAL DEFAULT 0"),
            ("carbs_g", "REAL DEFAULT 0"),
            ("fat_g", "REAL DEFAULT 0"),
            ("serving_size", "TEXT"),
            ("logged_at", "TIMESTAMP"),
        ]
        for col, typedef in new_cols:
            try:
                await conn.execute(text(f"ALTER TABLE food_entries ADD COLUMN {col} {typedef}"))
            except Exception:
                pass

        try:
            await conn.execute(text("ALTER TABLE exercise_entries ADD COLUMN intensity TEXT DEFAULT 'moderate'"))
        except Exception:
            pass

        new_user_cols = [
            ("email", "TEXT"),
            ("gender", "TEXT"),
            ("aim", "TEXT"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]
        for col, typedef in new_user_cols:
            try:
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {typedef}"))
            except Exception:
                pass


async def get_db():
    async with SessionLocal() as session:
        yield session
