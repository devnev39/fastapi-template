import jwt
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.models.user import User
from src.models.role import Role
from src.models.token import Token, TokenDecrypted
from src.db.query.users import get_user_by_username
from src.db.query.roles import get_role_db
from src.config.settings import settings
from src.core.logger.log import get_log, Log, app_logger


def get_logger(request: Request):
    logger = get_log(request=request)
    logger.update(log=Log(filename=__name__))
    request.state.logger = logger


router = APIRouter(dependencies=[Depends(get_logger)])


def create_token(user: User, role: Role) -> str:
    scopes = role.permissions
    userToken = TokenDecrypted(
        sub=user.username,
        role_id=str(role.id),
        scopes=scopes,
        user_id=str(user.id),
        exp=datetime.now() + timedelta(minutes=settings.TOKEN_EXPIRY_PERIOD),
    )
    encoded = jwt.encode(
        userToken.model_dump(),
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded


@router.post("")
async def login(
    formdata: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request
) -> Token:
    request.state.logger.update(Log(event=f"login - {formdata.username}"))
    # find user
    user = await get_user_by_username(formdata.username, request.app.state.db)
    request.state.logger.update(Log(msg="user found"))
    request.state.logger.update(Log(extra=str(user.model_dump())))
    # check user password

    if not user.verify_password(formdata.password):
        raise HTTPException(status_code=401, detail="Username or password incorrect !")
    # get the role
    role = await get_role_db(user.role_id, request.app.state.db)
    # make token
    token = create_token(user=user, role=role)
    request.state.logger.update(Log(msg="user found, login successfull"))
    app_logger.info(request.state.logger.model_dump())

    user = User(**user.model_dump())

    response = JSONResponse(
        status_code=200,
        content=Token(access_token=token, token_type="bearer", user=user).model_dump(),
    )
    response.set_cookie(key="Authorization", value=f"Bearer {token}")
    return response
