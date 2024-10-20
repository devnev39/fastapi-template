import pytest

from httpx import AsyncClient
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.models.role import Role, Permissions

pytestmark = pytest.mark.anyio


def get_role() -> dict:
    role = Role(id=str(ObjectId()), name="Level 1", permissions=Permissions.read_only)
    role = {**role.model_dump(), "password": "test"}
    return role


async def test_role_get_all(client: AsyncClient, db: AsyncIOMotorDatabase) -> None:
    response = await client.get("/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_role_post(client: AsyncClient) -> None:
    role = get_role()
    response = await client.post("/roles", json=role)
    print(response.json())
    assert response.status_code == 201
    # assert response.json() == Role(**role).model_dump(by_alias=True)


async def test_role_update(client: AsyncClient) -> None:
    role = get_role()
    response = await client.post("/roles", json=role)
    assert response.status_code == 201
    # assert response.json() == Role(**role).model_dump(by_alias=True)

    role = Role(**role).model_dump(by_alias=True)
    role["name"] = "Level 2"
    update = await client.patch(
        f"/roles/{role['_id']}",
        json=role,
    )
    assert update.status_code == 200
    # assert update.json() == role


async def test_role_delete(client: AsyncClient):
    role = get_role()
    response = await client.post("/roles", json=role)
    assert response.status_code == 201
    # assert response.json() == Role(**role).model_dump(by_alias=True)

    response = await client.delete(f"/roles/{role['id']}")
    assert response.status_code == 200
    assert response.json() == {"status": True}
