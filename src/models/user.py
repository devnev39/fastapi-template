from typing import Annotated

import bcrypt
from pydantic import (
    BeforeValidator,
    Field,
    SecretStr,
    field_serializer,
    field_validator,
)

from src.models.common import CommonMethods, CreatedAtProps, UpdatedAtProps

PyObjectId = Annotated[str, BeforeValidator(str)]


class User(CreatedAtProps, CommonMethods):
    id: PyObjectId | None = Field(
        description="Mongodb entity id", default=None, serialization_alias="_id",
    )
    username: str = Field(description="Username of user")
    name: str = Field(description="User name")
    role_id: str = Field(description="Role id", pattern=r"^[0-9a-f]{24}$")


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
                password.get_secret_value().encode("utf-8"), bcrypt.gensalt(),
            ).decode("utf-8"),
        )


# Used for internal intellisence
class UserOut(User):
    password: SecretStr = Field(description="User password")

    def verify_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.password.get_secret_value().encode("utf-8"),
        )


class UserUpdate(UpdatedAtProps):
    name: str | None = None
    role_id: str | None = None
