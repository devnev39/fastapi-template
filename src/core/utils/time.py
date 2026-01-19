from datetime import UTC, datetime


def get_utc_now() -> str:
    """Get utc now time."""
    return datetime.now(UTC).isoformat()


def get_timestamp() -> float:
    """Get utc timestamp."""
    return datetime.now(UTC).timestamp()
