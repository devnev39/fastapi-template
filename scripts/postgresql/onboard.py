from sqlalchemy import create_engine

from src.config.settings import settings
from src.models import Base, Role


async def create_root_user():
    pass


def create_tables():
    engine = create_engine(settings.CONNECTION_STRING)
    Role.metadata.create_all(engine)
    Base.metadata.create_all(engine)


create_tables()
