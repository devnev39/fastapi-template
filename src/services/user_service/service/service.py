from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.resource import ResourceNotFoundError
from src.models.user import User
from src.schemas.user import User as UserSchema
from src.schemas.user import UserUpdate as UserUpdateSchema


async def create_user_db(user: UserSchema, db: AsyncSession) -> User:
    new_user = User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_db(user_id: int, db: AsyncSession) -> User:
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise ResourceNotFoundError(
            resource_name=User.__name__,
            resource_id=f"{user_id!s}",
            event="src.services.user_service.service.service.get_user_db",
        )
    return user


async def get_user_by_username(username: str, db: AsyncSession) -> User:
    user = await db.scalar(select(User).where(User.username == username))
    if not user:
        raise ResourceNotFoundError(
            resource_name=User.__name__,
            resource_id=f"<username>{username}",
            event="src.services.user_service.service.service.get_user_by_username",
        )


async def get_all_users_db(db: AsyncSession) -> list[User]:
    return list((await db.scalars(select(User))).all())


async def update_user_db(
    user_id: int,
    user_update: UserUpdateSchema,
    db: AsyncSession,
) -> User:
    user = await get_user_db(user_id, db)
    if user_update.role_id:
        user.role_id = user_update.role_id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_db(user_id: int, db: AsyncSession):
    user = await get_user_db(user_id, db)
    await db.delete(user)
    await db.commit()
