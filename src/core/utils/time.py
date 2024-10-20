from datetime import datetime


def get_datetime_str() -> str:
    return datetime.now().isoformat()


def get_timestamp() -> float:
    return datetime.now().timestamp()
