from fastapi import APIRouter, Depends, Path, Request, Security

from src.models.token import TokenDecrypted
from src.core.security.get_current_user import get_current_user
from src.models.role import Role, RoleUpdate
from src.config.model_permissions import Role as available_scopes
from src.db.query.roles import (
    create_role_db,
    delete_role_db,
    get_role_db,
    get_roles_db,
    update_role_db,
)
from src.core.logger.log import Log, app_logger, get_log


def get_logger(request: Request):
    logger = get_log(request=request)
    logger.update(Log(filename=__name__))
    request.state.logger = logger


router = APIRouter(dependencies=[Depends(get_logger)])


@router.get("")
async def get_all_roles(
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> list[Role]:
    request.state.logger.update(Log(event="get all roles"))
    app_logger.debug(request.state.logger.model_dump())
    return await get_roles_db(db=request.app.state.db)


@router.get("/my-role")
async def get_my_role(
    request: Request,
    user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> Role:
    request.state.logger.update(Log(event="get my role"))
    role = await get_role_db(role_id=user.role_id, db=request.app.state.db)
    request.state.logger.update(Log(code=200))
    app_logger.debug(request.state.logger.model_dump())
    return role


@router.get("/{role_id}")
async def get_role(
    request: Request,
    role_id: str = Path(..., pattern=r"^[0-9a-f]{24}$"),
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> Role:
    request.state.logger.update(Log(event="get role"))
    role = await get_role_db(role_id=role_id, db=request.app.state.db)
    request.state.logger.update(Log(code=200))
    app_logger.debug(request.state.logger.model_dump())
    return role


@router.post("", status_code=201)
async def create_role(
    role: Role,
    request: Request,
    current_user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
) -> Role:
    request.state.logger.update(Log(event="create role"))
    role.created_by = current_user.sub
    role = await create_role_db(role=role, db=request.app.state.db)
    request.state.logger.update(Log(code=201, status="success"))
    app_logger.debug(request.state.logger.model_dump())
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
    request.state.logger.update(Log(event="update role"))
    role.updated_by = current_user.sub
    role_update = await update_role_db(
        role_id=role_id, role=role, db=request.app.state.db
    )
    request.state.logger.update(Log(status="success", code=200))
    app_logger.debug(request.state.logger.model_dump())
    return role_update


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
) -> dict:
    request.state.logger.update(Log(event="delete role"))
    await delete_role_db(role_id=role_id, db=request.app.state.db)
    request.state.logger.update(Log(code=200, status="success"))
    app_logger.debug(request.state.logger.model_dump())
    return {"status": True}
