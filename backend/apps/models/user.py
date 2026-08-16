from sqlalchemy import Integer, String, Column, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from apps.db.database import Base
from apps.schemas.role import Role


class User(Base):
    __tablename__="users"

    id=Column(Integer, nullable=False, primary_key=True, index=True, autoincrement=True)
    name=Column(String(100), nullable=False)
    email=Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age=Column(Integer, nullable=False)
    is_active=Column(Boolean, default=True, nullable=False)
    role = Column(Enum(Role, name="user_role"), nullable=False, default=Role.EMPLOYEE)
    profile_image = Column(String(500), nullable=True)
    employee = relationship(
            "Employee",
            back_populates="user",
            uselist=False,
    )
    created_at=Column(DateTime(
            timezone=True),
            server_default=func.now()
    )
    updated_at=Column(DateTime(
            timezone=True),
            default=func.now(),
            onupdate=func.now()
    )
