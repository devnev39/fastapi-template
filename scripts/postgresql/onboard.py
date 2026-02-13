import asyncio

from sqlalchemy import create_engine, select

from src.config.settings import settings
from src.core.logger.log import logger
from src.core.utils.encrypt import hash_password
from src.db.db import get_db_context
from src.models import Base, Role
from src.models.user import User


async def create_root_user(create_role: bool = True):
    """
    - role\n
    name: admin
    scopes: all
    - user\n
    username: root
    password: Rootpass@123
    """
    async with get_db_context() as db:
        role = None
        if create_role:
            role = Role(
                name="admin",
                scopes="user:read,user:write,role:read,role:write",
                created_by="System",
            )
            db.add(role)
            await db.commit()
            await db.refresh(role)
        else:
            role = await db.scalar(select(Role).where(Role.name == "admin"))
        if not role:
            raise Exception("Role not found !")
        user = User(
            username="root",
            password=hash_password("Rootpass@123"),
            role_id=role.id,
            created_by="System"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("Root user created...")


def create_tables():
    engine = create_engine(settings.CONNECTION_STRING)
    Role.metadata.create_all(engine)
    Base.metadata.create_all(engine)


asyncio.run(create_root_user())
