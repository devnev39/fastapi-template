from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.common import Creation, Timestamp
from src.models.role import Role


class User(Timestamp, Creation, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Role.id),
        nullable=False,
    )

    role: Mapped[Role] = relationship()
