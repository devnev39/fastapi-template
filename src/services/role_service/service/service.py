from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.resource import ResourceNotFoundError
from src.core.logger.spans import monitor
from src.models.role import Role
from src.schemas.role import Role as RoleSchema
from src.schemas.role import RoleUpdate as RoleUpdateSchema


@monitor
async def create_role_db(role: RoleSchema, db: AsyncSession) -> Role:
    new_role = Role(**role.model_dump())
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role


@monitor
async def get_role_db(role_id: int, db: AsyncSession) -> Role:
    role = await db.scalar(select(Role).where(Role.id == role_id))
    if not role:
        raise ResourceNotFoundError(
            resource_name=Role.__name__,
            resource_id=f"{role_id!s}",
            event="src.services.role_service.service.get_role_db",
        )
    return role


@monitor
async def get_roles_db(db: AsyncSession) -> list[Role]:
    return list((await db.scalars(select(Role))).all())


@monitor
async def update_role_db(
    role_id: int,
    role_update: RoleUpdateSchema,
    db: AsyncSession,
) -> Role:
    role = await get_role_db(role_id, db)
    if role_update.name:
        role.name = role_update.name

    if role_update.scopes:
        role.scopes = role_update.scopes
    return role


@monitor
async def delete_role_db(role_id: int, db: AsyncSession):
    role = await get_role_db(role_id, db)
    await db.delete(role)
