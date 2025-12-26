class ClientException(Exception):
    def __init__(self, status_code: int, event: str = None, *args: object) -> None:
        self.status_code = status_code
        self.event = event
        super().__init__(*args)
