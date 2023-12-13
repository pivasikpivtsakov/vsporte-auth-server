import enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import UserModel


class Roles(enum.StrEnum):
    unspecified = "unspecified"
    admin = "admin"
    client = "client"


class RoleInService(Base):
    __tablename__ = "roles_in_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["UserModel"] = relationship(back_populates="roles_in_services")
    role: Mapped[Roles]
    service: Mapped[str] = mapped_column(String(50))

    __table_args__ = (UniqueConstraint("user_id", "service", name="roles_in_services_user_id_service_key"),)
