from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.core.logger.log import logger
from src.core.utils.hash import verify_password
from src.core.utils.time import get_utc_now
from src.db.db import get_db
from src.models.role import Role
from src.models.user import User
from src.schemas.login import Login
from src.schemas.token import Token, TokenDecrypted
from src.schemas.user import User as UserSchema
from src.services.role_service.service.service import get_role_db
from src.services.user_service.service.service import get_user_by_username

router = APIRouter()


def create_token(user: User, role: Role) -> str:
    """Create token for user with role."""
    scopes = role.scopes.split(",")
    user_token = TokenDecrypted(
        sub=user.username,
        role_id=role.id,
        scopes=scopes,
        user_id=user.id,
        exp=get_utc_now() + timedelta(minutes=settings.TOKEN_EXPIRY_PERIOD),
    )
    return jwt.encode(
        user_token.model_dump(),
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


async def login(formdata: Login, db: AsyncSession) -> Token:
    """Return token with provided formadata and request."""
    # find user
    logger.info("auth.login.find_user")
    user = await get_user_by_username(formdata.username, db)
    # check user password

    logger.info("auth.login.check_password")
    if not verify_password(formdata.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrect !",
        )
    # get the role

    logger.info("auth.login.find_role")
    role = await get_role_db(user.role_id, db)

    # make token
    logger.info("auth.login.create_token")
    token = create_token(user=user, role=role)

    user_out = UserSchema.model_validate(user)

    return Token(access_token=token, token_type="bearer", user=user_out)


@router.post("", response_model=Token)
async def login_client(
    formdata: Login,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Login client with provided formdata."""
    logger.info("auth.login.start")
    token = await login(formdata, db)
    response.set_cookie(
        "Authorization",
        f"Bearer {token.access_token}",
        samesite="lax",
        secure=False,
        httponly=False,
    )
    return token


@router.post("/swagger", response_model=Token)
async def login_swagger(
    response: Response,
    formdata: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Perform login via swagger."""
    logger.info("auth.login_swagger.start")
    token = await login(
        Login(username=formdata.username, password=formdata.password),
        db,
    )
    response.set_cookie(key="Authorization", value=f"Bearer {token.access_token}")
    return token
