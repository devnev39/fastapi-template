from typing import Annotated

from fastapi import APIRouter, Depends, Path, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.model_permissions import User as UserPermissions
from src.core.logger.log import logger
from src.core.security.get_current_user import get_current_user
from src.db.db import get_db
from src.schemas.common import StatusResponse
from src.schemas.token import TokenDecrypted
from src.schemas.user import User, UserIn, UserUpdate
from src.services.role_service.service.service import get_role_db
from src.services.user_service.service.service import (
    create_user_db,
    delete_user_db,
    get_all_users_db,
    get_user_db,
    update_user_db,
)

router = APIRouter()


@router.get("", response_model=list[User])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[UserPermissions.permissions().read],
        ),
    ],
):
    logger.info("router.user.get_all_user")
    return await get_all_users_db(db=db)


@router.get("/me", response_model=User)
async def get_me(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[UserPermissions.permissions().read],
        ),
    ],
):
    logger.info("router.user.get_me")
    return await get_user_db(user_id=current_user.user_id, db=db)


@router.get("/{user_id}", response_model=User)
async def get_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Path(...)],
    _: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[UserPermissions.permissions().read],
        ),
    ],
):
    logger.info("router.user.get_user_by_id")
    return await get_user_db(user_id=user_id, db=db)


@router.post("", status_code=201, response_model=User)
async def create_user(
    user: UserIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[UserPermissions.permissions().write],
        ),
    ],
):
    logger.info("router.user.create_user")
    user.created_by = str(current_user.user_id)
    await get_role_db(user.role_id, db)
    return await create_user_db(user, db)


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[UserPermissions.permissions().write],
        ),
    ],
):
    logger.info("router.user.update_user")
    user.updated_by = current_user.sub
    return await update_user_db(
        user_id=user_id,
        user_update=user,
        db=db,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        TokenDecrypted,
        Security(
            get_current_user,
            scopes=[UserPermissions.permissions().write],
        ),
    ],
):
    logger.info("router.user.delete_user")
    await delete_user_db(user_id=user_id, db=db)
    return StatusResponse(status="True")
