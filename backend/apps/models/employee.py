from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from apps.db.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False
    )

    age = Column(Integer)

    designation = Column(
        String,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    user = relationship(
        "User",
        back_populates="employee",
    )

    department = relationship(
        "Department",
        back_populates="employees"
    )

    projects = relationship(
        "Project",
        secondary="employee_projects",
        back_populates="employees",
    )

    comments = relationship(
        "Comment",
        back_populates="employee",
    )

    assigned_issues = relationship(
        "Issue",
        foreign_keys="Issue.assignee_id",
        back_populates="assignee",
    )

    reported_issues = relationship(
        "Issue",
        foreign_keys="Issue.reporter_id",
        back_populates="reporter",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
