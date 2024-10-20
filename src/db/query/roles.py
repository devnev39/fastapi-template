from bson import ObjectId

from src.core.exceptions.resource import ResourceInsertionFailed, ResourceNotFound
from src.models.role import Role, RoleUpdate
from src.db.collections import collections
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_roles_db(db: AsyncIOMotorDatabase) -> list[Role]:
    roles_collection = db.get_collection(collections.roles_collection)
    roles = []
    async for r in roles_collection.find():
        roles.append(r)
    return [Role(**role) for role in roles]


async def get_role_db(role_id: str, db: AsyncIOMotorDatabase) -> Role:
    roles_collection = db.get_collection(collections.roles_collection)
    role = await roles_collection.find_one({"_id": ObjectId(role_id)})
    if not role:
        raise ResourceNotFound(resource_name="Role", resource_id=role_id)
    return Role(**role)


async def create_role_db(role: Role, db: AsyncIOMotorDatabase) -> Role:
    roles_collection = db.get_collection(collections.roles_collection)
    result = await roles_collection.insert_one(role.model_dump_mongo())
    if not result.inserted_id:
        raise ResourceInsertionFailed(resource_name="Role", resource_id=role.name)
    return await get_role_db(role_id=result.inserted_id, db=db)


async def update_role_db(
    role_id: str, role: RoleUpdate, db: AsyncIOMotorDatabase
) -> Role:
    roles_collection = db.get_collection(collections.roles_collection)
    await get_role_db(role_id=role_id, db=db)
    await roles_collection.update_one(
        {"_id": ObjectId(role_id)}, {"$set": role.model_dump()}
    )
    return await get_role_db(role_id=role_id, db=db)


async def delete_role_db(role_id: str, db: AsyncIOMotorDatabase) -> bool:
    roles_collection = db.get_collection(collections.roles_collection)
    await roles_collection.delete_one({"_id": ObjectId(role_id)})
    return True
