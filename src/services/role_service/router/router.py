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


router = APIRouter()


@router.get("")
async def get_all_roles(
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> list[Role]:
    return await get_roles_db(db=request.app.state.db)


@router.get("/my-role")
async def get_my_role(
    request: Request,
    user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> Role:
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
    await delete_role_db(role_id=role_id, db=request.app.state.db)
    return {"status": True}
