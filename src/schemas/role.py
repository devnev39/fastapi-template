from pydantic import BaseModel, ConfigDict, Field

from src.schemas.common import CreatedAtProps, UpdatedAtProps


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


class Role(CreatedAtProps):
    id: int | None = Field(
        default=None,
    )
    name: str = Field(description="Role name")
    scopes: str

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(UpdatedAtProps):
    name: str | None = Field(description="Role name", default=None)
    scopes: str | None = Field(description="Scopes", default=None)
