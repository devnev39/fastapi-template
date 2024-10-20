from pydantic import BaseModel
from datetime import datetime

from src.models.user import User


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenDecrypted(BaseModel):
    sub: str
    scopes: list[str]
    user_id: str
    role_id: str
    exp: datetime
