from typing import Annotated

from fastapi import APIRouter, Path, Request, Security

from src.config.model_permissions import Role as RolePermissions
from src.core.logger.log import logger
from src.core.security.get_current_user import get_current_user
from src.db.query.roles import (
    create_role_db,
    delete_role_db,
    get_role_db,
    get_roles_db,
    update_role_db,
)
from src.models.common import StatusResponse
from src.models.role import Role, RoleUpdate
from src.models.token import TokenDecrypted

router = APIRouter()


@router.get("")
async def get_all_roles(
    request: Request,
    _: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[RolePermissions.permissions().read],
    )],
) -> list[Role]:
    logger.info("router.role.get_all_roles")
    return await get_roles_db(db=request.app.state.db)


@router.get("/my-role")
async def get_my_role(
    request: Request,
    user: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[RolePermissions.permissions().read],
    )],
) -> Role:
    logger.info("router.role.get_my_role")
    return await get_role_db(role_id=user.role_id, db=request.app.state.db)


@router.get("/{role_id}")
async def get_role(
    request: Request,
    role_id: Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$")],
    _: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[RolePermissions.permissions().read],
    )],
) -> Role:
    logger.info("router.role.get_role_by_id")
    return await get_role_db(role_id=role_id, db=request.app.state.db)

@router.post("", status_code=201)
async def create_role(
    role: Role,
    request: Request,
    current_user: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[RolePermissions.permissions().write],
    )],
) -> Role:
    logger.info("router.role.create_role")
    role.created_by = current_user.sub
    return await create_role_db(role=role, db=request.app.state.db)


@router.patch("/{role_id}")
async def update_role(
    role_id: str,
    role: RoleUpdate,
    request: Request,
    current_user: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[RolePermissions.permissions().write],
    )],
) -> Role:
    logger.info("router.role.update_role")
    role.updated_by = current_user.sub
    return await update_role_db(
        role_id=role_id, role=role, db=request.app.state.db,
    )


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    request: Request,
    _: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[RolePermissions.permissions().write],
    )],
) -> StatusResponse:
    logger.info("router.role.delete_role")
    await delete_role_db(role_id=role_id, db=request.app.state.db)
    return StatusResponse(status="True")
