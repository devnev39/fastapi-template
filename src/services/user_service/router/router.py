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


def get_logger(request: Request):
    logger = get_log(request=request)
    logger.update(Log(filename=__name__))
    request.state.logger = logger


router = APIRouter(dependencies=[Depends(get_logger)])


@router.get("")
async def get_all_users(
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> list[User]:
    users = await get_all_users_db(db=request.app.state.db)
    request.state.logger.update(Log(code=200, event="get all users"))
    app_logger.debug(request.state.logger.model_dump())
    return users


@router.get("/me")
async def get_me(
    request: Request,
    current_user: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.read]
    ),
) -> User:
    request.state.logger.update(Log(event="get me"))
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
    request.state.logger.update(Log(event="get user"))
    user = await get_user_db(user_id=user_id, db=request.app.state.db)
    request.state.logger.update(Log(code=200))
    app_logger.debug(request.state.logger.model_dump())
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
    request.state.logger.update(Log(event="create user"))
    await get_role_db(user.role_id, request.app.state.db)
    user_new = await create_user_db(user, db=request.app.state.db)
    request.state.logger.update(Log(code=201, status="success"))
    app_logger.debug(request.state.logger.model_dump())
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
    request.state.logger.update(Log(event="update user"))
    user_update = await update_user_db(
        user_id=user_id, user=user, db=request.app.state.db
    )
    request.state.logger.update(Log(code=200, status="success"))
    app_logger.debug(request.state.logger.model_dump())
    return user_update


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    _: TokenDecrypted = Security(
        get_current_user, scopes=[available_scopes.permissions.write]
    ),
):
    request.state.logger.update(Log(event="update user"))
    result = await delete_user_db(user_id=user_id, db=request.app.state.db)
    request.state.logger.update(Log(code=200, status="success"))
    return {"status": result}
