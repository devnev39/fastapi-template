from datetime import UTC, datetime


def get_utc_now() -> datetime:
    """Get utc now time."""
    return datetime.now(UTC)


def get_timestamp() -> float:
    """Get utc timestamp."""
    return datetime.now(UTC).timestamp()
