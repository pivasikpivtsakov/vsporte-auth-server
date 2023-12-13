from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, relationship, Mapped

from .base import Base

if TYPE_CHECKING:
    from .role_in_service import RoleInService


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(300))

    # user cannot have more than 1 role in 1 service
    # model: user to roles in services
    roles_in_services: Mapped[list["RoleInService"]] = relationship(back_populates="user", cascade="all, delete-orphan")
