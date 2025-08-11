from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

class Base(DeclarativeBase):
    pass

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        url = settings.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        _engine = create_async_engine(url, echo=False, future=True)
    return _engine


def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _SessionLocal


async def get_db_session():
    if not settings.use_db:
        raise RuntimeError("Database disabled. Set APP_USE_DB=true to enable.")
    async_session = get_sessionmaker()
    async with async_session() as session:
        yield session