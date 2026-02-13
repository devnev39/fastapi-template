from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schemas.user import User


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

    model_config = ConfigDict(from_attributes=True)


class TokenDecrypted(BaseModel):
    sub: str
    scopes: list[str]
    user_id: int
    role_id: int
    exp: datetime
