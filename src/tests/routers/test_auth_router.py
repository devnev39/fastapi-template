import pytest

from bson import ObjectId
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.models.user import User

pytestmark = pytest.mark.anyio


async def test_auth_router(
    client: AsyncClient, user: User, db: AsyncIOMotorDatabase
) -> None:
    role = await db.get_collection("roles").find_one({"_id": ObjectId(user.role_id)})
    assert role

    response = await client.post(
        "/auth", data={"username": user.username, "password": "123"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_auth_router_fail(
    client: AsyncClient, user: User, db: AsyncIOMotorDatabase
) -> None:
    role = await db.get_collection("roles").find_one({"_id": ObjectId(user.role_id)})
    assert role

    response = await client.post(
        "/auth", data={"username": user.username, "password": "wrong"}
    )
    assert response.status_code == 401
