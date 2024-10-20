import pytest

from httpx import AsyncClient

from src.models.role import Role
from src.tests.utils.routers import get_user

pytestmark = pytest.mark.anyio


async def test_user_get_all(client: AsyncClient) -> None:
    response = await client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_user_post(client: AsyncClient, role: Role) -> None:
    user = get_user(role_id=str(role.id))
    response = await client.post("/users", json=user.model_dump())
    assert response.status_code == 201
    assert response.json()


async def test_user_update(client: AsyncClient, role: Role) -> None:
    user = get_user(role_id=str(role.id))
    response = await client.post("/users", json=user.model_dump())
    assert response.status_code == 201
    assert response.json()

    user = user.model_dump(by_alias=True)
    user["name"] = "Tester Updated"
    update = await client.patch(
        f"/users/{user['_id']}",
        json=user,
    )
    assert update.status_code == 200
    assert update.json()


async def test_user_delete(client: AsyncClient, role: Role):
    user = get_user(role_id=str(role.id))
    response = await client.post("/users", json=user.model_dump(by_alias=True))
    assert response.status_code == 201
    assert response.json()

    response = await client.delete(f"/users/{user.id}")
    assert response.status_code == 200
    assert response.json() == {"status": True}
