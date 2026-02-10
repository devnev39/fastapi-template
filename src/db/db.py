import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

engine = create_async_engine(settings.CONNECTION_STRING)

session = async_sessionmaker(engine, expire_on_commit=False)


@contextlib.asynccontextmanager
async def get_db() -> AsyncIterator[AsyncSession]:
    db = session()
    try:
        yield db
    except Exception:
        await db.rollback()
    finally:
        await db.close()
