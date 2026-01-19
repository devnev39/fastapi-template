class Permissions:
    def __init__(self, model: type):
        self.model = model

    @property
    def read(self):
        return f"{self.model.__name__.lower()}:read"

    @property
    def write(self):
        return f"{self.model.__name__.lower()}:write"


class PermissionProvider:
    @classmethod
    def permissions(cls):
        return Permissions(cls)
