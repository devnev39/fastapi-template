from fastapi import APIRouter, Depends, Path, Request, Security

from src.core.security.get_current_user import get_current_user
from src.db.query.users import (
    create_user_db,
    delete_user_db,
    get_all_users_db,
    get_user_db,
    update_user_db,
)
from src.db.query.roles import get_role_db
from src.models.token import TokenDecrypted
from src.config.model_permissions import User as available_scopes
from src.models.user import User, UserIn, UserUpdate
from src.core.logger.log import Log, app_logger, get_log

router = APIRouter()


@router.get("")
async def get_all_users(
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> list[User]:
    users = await get_all_users_db(db=request.app.state.db)
    return users


@router.get("/me")
async def get_me(
    request: Request,
    current_user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> User:
    user = await get_user_db(user_id=current_user.user_id, db=request.app.state.db)
    return user


@router.get("/{user_id}")
async def get_user(
    request: Request,
    user_id: str = Path(..., pattern=r"^[0-9a-f]{24}$"),
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> User:
    user = await get_user_db(user_id=user_id, db=request.app.state.db)
    return user


@router.post("", status_code=201)
async def create_user(
    user: UserIn,
    request: Request,
    current_user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
) -> User:
    user.created_by = current_user.user_id
    await get_role_db(user.role_id, request.app.state.db)
    user_new = await create_user_db(user, db=request.app.state.db)
    return user_new


@router.patch("/{user_id}")
async def update_user(
    user_id: str,
    user: UserUpdate,
    request: Request,
    current_user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
) -> User:
    user.updated_by = current_user.sub
    user_update = await update_user_db(
        user_id=user_id, user=user, db=request.app.state.db
    )
    return user_update


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
):
    result = await delete_user_db(user_id=user_id, db=request.app.state.db)
    return {"status": result}
