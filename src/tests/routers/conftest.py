# ruff: noqa
import os
import pymongo

from datetime import datetime, timedelta
from bson import ObjectId

from src.models.token import TokenDecrypted
from src.core.security.get_current_user import get_current_user
from src.tests.utils.routers import get_role, get_user

os.environ["ENV"] = "test"
os.environ["DB_NAME"] = "testing-db"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["APP_LOGGER_SYS_LOG"] = "False"

from src.config.settings import Settings

settings = Settings()

from typing import AsyncIterator
from httpx import AsyncClient
import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.models.role import Role
from src.models.user import User
from src.main import app


sync_db_client = pymongo.MongoClient(settings.MONGO_URI)
names = sync_db_client.list_database_names()
if settings.DB_NAME in names:
    raise Exception(
        f"Database used for testing named {settings.DB_NAME} already exists!"
    )


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def db():
    db_client = AsyncIOMotorClient(settings.MONGO_URI)
    return db_client.get_database(settings.DB_NAME)


@pytest.fixture(scope="session")
async def role(db: AsyncIOMotorDatabase) -> Role:
    await db.get_collection("roles").drop()
    role = get_role()
    print(role.model_dump_mongo())
    role = await db.get_collection("roles").insert_one(role.model_dump_mongo())
    role = await db.get_collection("roles").find_one(
        {"_id": ObjectId(role.inserted_id)}
    )
    return Role(**role)


@pytest.fixture(scope="session")
async def user(db: AsyncIOMotorDatabase, role: Role) -> User:
    await db.get_collection("users").drop()
    user = get_user(role_id=role.id)
    user = await db.get_collection("users").insert_one(user.model_dump_mongo())
    user = await db.get_collection("users").find_one(
        {"_id": ObjectId(user.inserted_id)}
    )
    return User(**user)


def get_token_user(user: User, role: Role):
    def wrapper():
        return TokenDecrypted(
            sub=user.username,
            user_id=str(user.id),
            role_id=str(role.id),
            exp=datetime.now() + timedelta(days=1),
            scopes=role.permissions,
        )

    return wrapper


@pytest.fixture(scope="session")
async def client(db: AsyncIOMotorDatabase, user: User) -> AsyncIterator[AsyncClient]:
    role = await db.get_collection("roles").find_one({"_id": ObjectId(user.role_id)})
    app.state.db = db
    app.dependency_overrides[get_current_user] = get_token_user(user, Role(**role))
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
    await AsyncIOMotorClient(settings.MONGO_URI).drop_database("testing-db")
