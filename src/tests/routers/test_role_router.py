# ruff: noqa: S101
import pytest
from bson import ObjectId
from fastapi import status
from httpx import AsyncClient

from src.models.role import Permissions, Role

pytestmark = pytest.mark.anyio


def get_role() -> dict:
    role = Role(id=str(ObjectId()), name="Level 1", permissions=Permissions.read_only())
    return {**role.model_dump(), "password": "test"}


async def test_role_get_all(client: AsyncClient) -> None:
    response = await client.get("/roles")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


async def test_role_post(client: AsyncClient) -> None:
    role = get_role()
    response = await client.post("/roles", json=role)
    assert response.status_code == status.HTTP_201_CREATED


async def test_role_update(client: AsyncClient) -> None:
    role = get_role()
    response = await client.post("/roles", json=role)
    assert response.status_code == status.HTTP_201_CREATED

    role = Role(**role).model_dump(by_alias=True)
    role["name"] = "Level 2"
    update = await client.patch(
        f"/roles/{role['_id']}",
        json=role,
    )
    assert update.status_code == status.HTTP_200_OK


async def test_role_delete(client: AsyncClient):
    role = get_role()
    response = await client.post("/roles", json=role)
    assert response.status_code == status.HTTP_201_CREATED

    response = await client.delete(f"/roles/{role['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": True}
