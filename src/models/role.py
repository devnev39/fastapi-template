from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.common import Creation, Timestamp


class Role(Timestamp, Creation, Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    scopes: Mapped[str] = mapped_column(String)
