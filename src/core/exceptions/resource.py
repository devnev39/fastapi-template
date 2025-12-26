from src.core.exceptions.client_exception import ClientException


class ResourceException(ClientException):
    def __init__(
        self, resource_name: str, resource_id: str, status_code: int, event: str = None
    ) -> None:
        self.resource_name = resource_name
        self.resource_id = resource_id
        self.status_code = status_code
        super().__init__(status_code=status_code, event=event)


class ResourceNotFound(ResourceException):
    def __init__(
        self,
        resource_name: str,
        resource_id: str,
        status_code: int = 404,
        event: str = None,
    ) -> None:
        super().__init__(
            resource_name, resource_id, status_code=status_code, event=event
        )

    def __str__(self) -> str:
        return f"Resource {self.resource_name} - {self.resource_id} not found!"


class ResourceInsertionFailed(ResourceException):
    def __init__(
        self,
        resource_name: str,
        resource_id: str,
        status_code: int = 500,
        event: str = None,
    ) -> None:
        super().__init__(
            resource_name, resource_id, status_code=status_code, event=event
        )

    def __str__(self) -> str:
        return f"Resource {self.resource_name} - {self.resource_id} insertion failed!"
