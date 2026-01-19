
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param

from src.config.settings import settings
from src.core.logger.log import logger
from src.models.token import TokenDecrypted


class OAuth2PasswordBearerCookie(OAuth2):
    """oauth 2 password bearer cookie class"""

    def __init__(
        self,
        token_url: str,
        scheme_name: str = "",
        scopes: dict = {},
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        header_authorization: str = request.headers.get("Authorization", "")
        cookie_authorization: str = request.cookies.get("Authorization", "")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization,
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization,
        )
        scheme, param = "", ""

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated",
                )
            return None
        return param


oauth2_scheme = OAuth2PasswordBearerCookie("auth")


async def get_current_user(
    _: Request,
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = jwt.decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
    if user is None:
        logger.warning(event="app.security.token_error")
        raise credentials_exception
    user = TokenDecrypted(**user)
    if security_scopes.scopes:
        for scope in security_scopes.scopes:
            if scope not in user.scopes:
                logger.warning(event="app.security.forbidden", status_code=403)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions",
                )
    return user
