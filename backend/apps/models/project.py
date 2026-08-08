from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    func,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from apps.db.database import Base
from apps.schemas.project import ProjectStatus


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    description = Column(Text)

    status = Column(
        Enum(ProjectStatus),
        nullable=False,
        default=ProjectStatus.PLANNING,
    )

    owner_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
    )

    employees = relationship(
        "Employee",
        secondary="employee_projects",
        back_populates="projects",
    )

    issues = relationship(
        "Issue",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    owner = relationship(
        "Employee",
        foreign_keys=[owner_id],
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
