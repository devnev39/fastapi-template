import jwt
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.models.login import Login
from src.models.user import User
from src.models.role import Role
from src.models.token import Token, TokenDecrypted
from src.db.query.users import get_user_by_username
from src.db.query.roles import get_role_db
from src.config.settings import settings


router = APIRouter()


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


async def login(formdata: Login, request: Request) -> Token:
    # find user
    user = await get_user_by_username(formdata.username, request.app.state.db)
    # check user password

    if not user.verify_password(formdata.password):
        raise HTTPException(status_code=401, detail="Username or password incorrect !")
    # get the role
    role = await get_role_db(user.role_id, request.app.state.db)
    # make token
    token = create_token(user=user, role=role)

    user = User(**user.model_dump())

    return Token(access_token=token, token_type="bearer", user=user)


@router.post("", response_model=Token)
async def login_client(formdata: Login, request: Request):
    return await login(formdata, request)


@router.post("/swagger", response_model=Token)
async def login_swagger(
    formdata: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request
):
    token = await login(
        Login(username=formdata.username, password=formdata.password), request
    )
    response = JSONResponse(status_code=200, content=token)
    response.set_cookie(key="Authorization", value=f"Bearer {token.access_token}")
    return response
