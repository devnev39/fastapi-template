from pymongo.mongo_client import MongoClient

from src.config.settings import settings
from src.db.collections import collections
from src.models.role import Role, Permissions
from src.models.user import UserIn

client = MongoClient(settings.MONGO_URI)
db = client.get_database(settings.DB_NAME)

user_collection = db.get_collection(collections.users_collection)
role_collection = db.get_collection(collections.roles_collection)

role = role_collection.find_one({"name": "root"})

if role:
    print("Role already exists !")
else:
    role = Role(name="root", permissions=Permissions.root_user)
    role_collection.insert_one(role.model_dump_mongo())
    role = role_collection.find_one({"name": "root"})

user = user_collection.find_one({"username": settings.ROOT_USERNAME.get_secret_value()})

if user:
    raise Exception("Root user already exist !")
else:
    user = UserIn(
        name="root",
        username=settings.ROOT_USERNAME.get_secret_value(),
        role_id=str(role["_id"]),
        password=settings.ROOT_PASSWORD.get_secret_value(),
    )
    user_collection.insert_one(user.model_dump_mongo())
    user = user_collection.find_one(
        {"username": settings.ROOT_USERNAME.get_secret_value()}
    )

    print("Root user created !")
