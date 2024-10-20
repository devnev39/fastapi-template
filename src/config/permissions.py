from typing import Type


class Permissions:
    def __init__(self, model: Type):
        self.model = model

    @property
    def read(self):
        return f"{self.model.__name__.lower()}:read"

    @property
    def write(self):
        return f"{self.model.__name__.lower()}:write"


class PermissionProvider:
    @classmethod
    @property
    def permissions(cls):
        return Permissions(cls)
