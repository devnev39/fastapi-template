from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from src.models.common import CommonMethods, CreatedAtProps, UpdatedAtProps

PyObjectId = Annotated[str, BeforeValidator(str)]


class Permissions(BaseModel):
    user: list[str] = ["read", "write"]
    role: list[str] = ["read", "write"]

    @classmethod
    def read_only(cls):
        read_scopes = []
        for entity, scopes in cls.model_fields.items():
            if "read" in scopes.default:
                read_scopes.append(f"{entity}:read")
        return read_scopes

    @classmethod
    def root_user(cls):
        root_scopes = []
        for field, scopes in cls.model_fields.items():
            root_scopes.extend([f"{field}:{scope}" for scope in scopes.default])
        return root_scopes


class Role(CreatedAtProps, CommonMethods):
    id: PyObjectId | None = Field(
        description="Mongodb entity id", serialization_alias="_id", default=None,
    )
    name: str = Field(description="Role name")
    permissions: list[str]


class RoleUpdate(UpdatedAtProps):
    name: str | None = Field(description="Role name", default=None)
    permissions: list[str] | None = Field(description="Permissions", default=None)
