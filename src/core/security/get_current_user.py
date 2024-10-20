import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2, SecurityScopes
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional
from pydantic import ValidationError

from src.config.settings import settings
from src.core.exceptions.token_exception import TokenException
from src.core.logger.log import Log, app_logger
from src.models.token import TokenDecrypted


class OAuth2PasswordBearerCookie(OAuth2):
    """oauth 2 password bearer cookie class"""

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = "",
        scopes: dict = {},
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization", "")
        cookie_authorization: str = request.cookies.get("Authorization", "")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
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
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
                )
            return None
        return param


oauth2_scheme = OAuth2PasswordBearerCookie("auth")


async def get_current_user(
    request: Request,
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = jwt.decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
        if user is None:
            request.state.logger.update(Log(code=401, error="Invalid token"))
            app_logger.warning(request.state.logger.model_dump())
            raise credentials_exception
        user = TokenDecrypted(**user)
        if security_scopes.scopes:
            for scope in security_scopes.scopes:
                if scope not in user.scopes:
                    request.state.logger.update(
                        Log(
                            code=403,
                            error="Not enough permissions",
                            extra=f"scope missing - {scope} | User - {user.user_id} | Resource - {request.method} {request.url.path}",
                        )
                    )
                    app_logger.warning(request.state.logger.model_dump())
                    raise HTTPException(
                        status_code=403, detail="Not enough permissions"
                    )
        return user
    except HTTPException as ex:
        # If the token is not valid then only this exception will be raised
        raise ex
    except (TypeError, ValidationError) as ex:
        # If the token user is not validated with pydantic it's internal server error due to
        # preprocessing of token by the server
        request.state.logger.update(Log(code=500, error=str(ex)))
        app_logger.error(request.state.logger.model_dump(), exc_info=ex)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as ex:
        # Other than that all other exceptions are raised as TokenException
        request.state.logger.update(Log(code=401, error=str(ex)))
        app_logger.warning(request.state.logger.model_dump(), exc_info=ex)
        raise TokenException(ex)
