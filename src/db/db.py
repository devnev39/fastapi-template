from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

engine = create_async_engine(settings.CONNECTION_STRING)

session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    db = session()
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


@asynccontextmanager
async def get_db_context() -> AsyncIterator[AsyncSession]:
    db = session()
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


