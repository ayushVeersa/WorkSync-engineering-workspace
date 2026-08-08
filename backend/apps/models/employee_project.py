from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime

from apps.db.database import Base


class EmployeeProject(Base):
    __tablename__ = "employee_projects"

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        primary_key=True,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        primary_key=True,
    )

    assigned_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )