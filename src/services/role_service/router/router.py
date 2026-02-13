from typing import Annotated

from fastapi import APIRouter, Depends, Path, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.model_permissions import Role as RolePermissions
from src.core.logger.log import logger
from src.core.security.get_current_user import get_current_user
from src.db.db import get_db
from src.schemas.common import StatusResponse
from src.schemas.role import Role, RoleUpdate
from src.schemas.token import TokenDecrypted
from src.services.role_service.service.service import (
    create_role_db,
    delete_role_db,
    get_role_db,
    get_roles_db,
    update_role_db,
)

router = APIRouter()


@router.get("", response_model=list[Role])
async def get_all_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[RolePermissions.permissions().read],
        ),
    ],
):
    logger.info("router.role.get_all_roles")
    return await get_roles_db(db=db)


@router.get("/my-role", response_model=Role)
async def get_my_role(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[RolePermissions.permissions().read],
        ),
    ],
):
    logger.info("router.role.get_my_role")
    return await get_role_db(role_id=int(user.role_id), db=db)


@router.get("/{role_id}", response_model=Role)
async def get_role(
    db: Annotated[AsyncSession, Depends(get_db)],
    role_id: Annotated[int, Path(...)],
    _: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[RolePermissions.permissions().read],
        ),
    ],
):
    logger.info("router.role.get_role_by_id")
    return await get_role_db(role_id=role_id, db=db)


@router.post("", status_code=201, response_model=Role)
async def create_role(
    role: Role,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[RolePermissions.permissions().write],
        ),
    ],
):
    logger.info("router.role.create_role")
    role.created_by = current_user.sub
    return await create_role_db(role=role, db=db)


@router.patch("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[RolePermissions.permissions().write],
        ),
    ],
):
    logger.info("router.role.update_role")
    role.updated_by = current_user.sub
    return await update_role_db(
        role_id=role_id,
        role_update=role,
        db=db,
    )


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[RolePermissions.permissions().write],
        ),
    ],
) -> StatusResponse:
    logger.info("router.role.delete_role")
    await delete_role_db(role_id=role_id, db=db)
    return StatusResponse(status="True")
