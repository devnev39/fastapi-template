from fastapi import APIRouter
from fastapi import Path
from fastapi import Request
from fastapi import Security

from src.config.model_permissions import Role as available_scopes
from src.core.logger.log import logger
from src.core.security.get_current_user import get_current_user
from src.db.query.roles import create_role_db
from src.db.query.roles import delete_role_db
from src.db.query.roles import get_role_db
from src.db.query.roles import get_roles_db
from src.db.query.roles import update_role_db
from src.models.role import Role
from src.models.role import RoleUpdate
from src.models.token import TokenDecrypted

router = APIRouter()


@router.get("")
async def get_all_roles(
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> list[Role]:
    logger.info("router.role.get_all_roles")
    return await get_roles_db(db=request.app.state.db)


@router.get("/my-role")
async def get_my_role(
    request: Request,
    user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> Role:
    logger.info("router.role.get_my_role")
    role = await get_role_db(role_id=user.role_id, db=request.app.state.db)
    return role


@router.get("/{role_id}")
async def get_role(
    request: Request,
    role_id: str = Path(..., pattern=r"^[0-9a-f]{24}$"),
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> Role:
    logger.info("router.role.get_role_by_id")
    role = await get_role_db(role_id=role_id, db=request.app.state.db)
    return role


@router.post("", status_code=201)
async def create_role(
    role: Role,
    request: Request,
    current_user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
) -> Role:
    logger.info("router.role.create_role")
    role.created_by = current_user.sub
    role = await create_role_db(role=role, db=request.app.state.db)
    return role


@router.patch("/{role_id}")
async def update_role(
    role_id: str,
    role: RoleUpdate,
    request: Request,
    current_user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
) -> Role:
    logger.info("router.role.update_role")
    role.updated_by = current_user.sub
    role_update = await update_role_db(
        role_id=role_id, role=role, db=request.app.state.db
    )
    return role_update


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
) -> dict:
    logger.info("router.role.delete_role")
    await delete_role_db(role_id=role_id, db=request.app.state.db)
    return {"status": True}
