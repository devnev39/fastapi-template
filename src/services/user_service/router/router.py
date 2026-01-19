from typing import Annotated

from fastapi import APIRouter, Path, Request, Security

from src.config.model_permissions import User as UserPermissions
from src.core.logger.log import logger
from src.core.security.get_current_user import get_current_user
from src.db.query.roles import get_role_db
from src.db.query.users import (
    create_user_db,
    delete_user_db,
    get_all_users_db,
    get_user_db,
    update_user_db,
)
from src.models.common import StatusResponse
from src.models.token import TokenDecrypted
from src.models.user import User, UserIn, UserUpdate

router = APIRouter()


@router.get("")
async def get_all_users(
    request: Request,
    _: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[UserPermissions.permissions().read],
    )],
) -> list[User]:
    logger.info("router.user.get_all_user")
    return await get_all_users_db(db=request.app.state.db)


@router.get("/me")
async def get_me(
    request: Request,
    current_user: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[UserPermissions.permissions().read],
    )],
) -> User:
    logger.info("router.user.get_me")
    return await get_user_db(user_id=current_user.user_id, db=request.app.state.db)


@router.get("/{user_id}")
async def get_user(
    request: Request,
    user_id: Annotated[str, Path(..., pattern=r"^[0-9a-f]{24}$")],
    _: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[UserPermissions.permissions().read],
    )],
) -> User:
    logger.info("router.user.get_user_by_id")
    return await get_user_db(user_id=user_id, db=request.app.state.db)


@router.post("", status_code=201)
async def create_user(
    user: UserIn,
    request: Request,
    current_user: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[UserPermissions.permissions().write],
    )],
) -> User:
    logger.info("router.user.create_user")
    user.created_by = current_user.user_id
    await get_role_db(user.role_id, request.app.state.db)
    return await create_user_db(user, db=request.app.state.db)


@router.patch("/{user_id}")
async def update_user(
    user_id: str,
    user: UserUpdate,
    request: Request,
    current_user: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[UserPermissions.permissions().write],
    )],
) -> User:
    logger.info("router.user.update_user")
    user.updated_by = current_user.sub
    return await update_user_db(
        user_id=user_id, user=user, db=request.app.state.db,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    _: Annotated[TokenDecrypted, Security(
        get_current_user, scopes=[UserPermissions.permissions().write],
    )],
):
    logger.info("router.user.delete_user")
    await delete_user_db(user_id=user_id, db=request.app.state.db)
    return StatusResponse(status="True")
