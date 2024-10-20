from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field

from src.models.common import CreatedAtProps, UpdatedAtProps, CommonMethods

PyObjectId = Annotated[str, BeforeValidator(str)]


class Permissions(BaseModel):
    user: list[str] = ["read", "write"]
    role: list[str] = ["read", "write"]

    @classmethod
    @property
    def read_only(cls):
        read_scopes = []
        for entity, scopes in cls.model_fields.items():
            if "read" in scopes.default:
                read_scopes.append(f"{entity}:read")
        return read_scopes

    @classmethod
    @property
    def root_user(cls):
        root_scopes = []
        for field, scopes in cls.model_fields.items():
            root_scopes.extend([f"{field}:{scope}" for scope in scopes.default])
        return root_scopes


class Role(CreatedAtProps, CommonMethods):
    id: Optional[PyObjectId] = Field(
        description="Mongodb entity id", serialization_alias="_id", default=None
    )
    name: str = Field(description="Role name")
    permissions: list[str]


class RoleUpdate(UpdatedAtProps):
    name: Optional[str] = Field(description="Role name", default=None)
    permissions: Optional[list[str]] = Field(description="Permissions", default=None)
