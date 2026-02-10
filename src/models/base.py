from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    __table_args__ = {
        "schema": "template",
    }
