import bcrypt
from pydantic import (
    Field,
    SecretStr,
    field_serializer,
    field_validator,
)

from src.schemas.common import CreatedAtProps, UpdatedAtProps


class User(CreatedAtProps):
    id: int | None = Field(
        default=None,
    )
    username: str = Field(description="Username of user")
    name: str = Field(description="User name")
    role_id: int = Field(description="Role id", pattern=r"^\d+$")


class UserIn(User):
    password: SecretStr = Field(description="User password")

    @field_serializer("password", when_used="always")
    def dump_secret(self, v: SecretStr):
        return v.get_secret_value()

    @field_validator("password")
    @classmethod
    def hash_password(cls, password: SecretStr) -> SecretStr:
        return SecretStr(
            bcrypt.hashpw(
                password.get_secret_value().encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8"),
        )


# Used for internal intellisence
class UserOut(User):
    password: SecretStr = Field(description="User password")


class UserUpdate(UpdatedAtProps):
    name: str | None = None
    role_id: int | None = None
