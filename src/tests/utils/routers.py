from bson import ObjectId
from src.models.role import Role, Permissions
from src.models.user import UserIn


def get_role(name: str = "Root"):
    return Role(id=str(ObjectId()), name=name, permissions=Permissions.root_user)


def get_user(role_id: str):
    return UserIn(
        id=str(ObjectId()),
        username="test_user",
        name="Tester",
        role_id=role_id,
        password="123",
    )
