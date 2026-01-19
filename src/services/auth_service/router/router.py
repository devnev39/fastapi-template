from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.config.settings import settings
from src.core.logger.log import logger
from src.core.utils.time import get_utc_now
from src.db.query.roles import get_role_db
from src.db.query.users import get_user_by_username
from src.models.login import Login
from src.models.role import Role
from src.models.token import Token, TokenDecrypted
from src.models.user import User

router = APIRouter()


def create_token(user: User, role: Role) -> str:
    """Create token for user with role."""
    scopes = role.permissions
    user_token = TokenDecrypted(
        sub=user.username,
        role_id=str(role.id),
        scopes=scopes,
        user_id=str(user.id),
        exp=get_utc_now() + timedelta(minutes=settings.TOKEN_EXPIRY_PERIOD),
    )
    return jwt.encode(
        user_token.model_dump(),
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


async def login(formdata: Login, request: Request) -> Token:
    """Return token with provided formadata and request."""
    # find user
    logger.info("auth.login.find_user")
    user = await get_user_by_username(formdata.username, request.app.state.db)
    # check user password

    logger.info("auth.login.check_password")
    if not user.verify_password(formdata.password):
        raise HTTPException(status_code=401, detail="Username or password incorrect !")
    # get the role

    logger.info("auth.login.find_role")
    role = await get_role_db(user.role_id, request.app.state.db)

    # make token
    logger.info("auth.login.create_token")
    token = create_token(user=user, role=role)

    user = User(**user.model_dump())

    return Token(access_token=token, token_type="bearer", user=user)


@router.post("")
async def login_client(formdata: Login, request: Request) -> Token:
    """Login client with provided formdata."""
    logger.info("auth.login.start")
    return await login(formdata, request)


@router.post("/swagger")
async def login_swagger(
    formdata: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
) -> Token:
    """Perform login via swagger."""
    logger.info("auth.login_swagger.start")
    token = await login(
        Login(username=formdata.username, password=formdata.password),
        request,
    )
    response = JSONResponse(status_code=200, content=token)
    response.set_cookie(key="Authorization", value=f"Bearer {token.access_token}")
    return response
