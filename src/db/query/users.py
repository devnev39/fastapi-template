from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.exceptions.resource import ResourceInsertionFailed
from src.core.exceptions.resource import ResourceNotFound
from src.core.logger.spans import monitor
from src.db.collections import collections
from src.models.user import User
from src.models.user import UserIn
from src.models.user import UserOut
from src.models.user import UserUpdate


@monitor
async def get_all_users_db(db: AsyncIOMotorDatabase) -> list[User]:
    users_collection = db.get_collection(collections.users_collection)
    users = []
    async for u in users_collection.find({}):
        users.append(u)
    return [User(**user) for user in users]


@monitor
async def get_user_by_username(username: str, db: AsyncIOMotorDatabase) -> UserOut:
    users_collection = db.get_collection(collections.users_collection)
    user = await users_collection.find_one({"username": username})
    if not user:
        raise ResourceNotFound(
            resource_name="User", resource_id=username, event="db.user.find_user"
        )
    return UserOut(**user)


@monitor
async def get_user_db(user_id: str, db: AsyncIOMotorDatabase) -> User:
    users_collection = db.get_collection(collections.users_collection)
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise ResourceNotFound(
            resource_name="User", resource_id=user_id, event="db.user.find_user"
        )
    return user


@monitor
async def create_user_db(user: UserIn, db: AsyncIOMotorDatabase) -> User:
    users_collection = db.get_collection(collections.users_collection)
    result = await users_collection.insert_one(user.model_dump_mongo())
    if not result.inserted_id:
        raise ResourceInsertionFailed(
            resource_name="User", resource_id=user.name, event="db.user.insert_user"
        )
    return await get_user_db(result.inserted_id, db)


@monitor
async def update_user_db(
    user_id: str, user: UserUpdate, db: AsyncIOMotorDatabase
) -> User:
    users_collection = db.get_collection(collections.users_collection)
    await get_user_db(user_id=user_id, db=db)
    await users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user.model_dump()}
    )
    return await get_user_db(user_id=user_id, db=db)


@monitor
async def delete_user_db(user_id: str, db: AsyncIOMotorDatabase) -> bool:
    users_collection = db.get_collection(collections.users_collection)
    await users_collection.delete_one({"_id": ObjectId(user_id)})
    return True
