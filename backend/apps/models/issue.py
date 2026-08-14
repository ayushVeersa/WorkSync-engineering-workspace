from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from apps.db.database import Base
from apps.schemas.issue import (
    IssueType,
    IssueStatus,
    IssuePriority,
)


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    description = Column(Text)

    issue_type = Column(
        Enum(IssueType),
        nullable=False,
        default=IssueType.TASK,
    )

    priority = Column(
        Enum(IssuePriority),
        nullable=False,
        default=IssuePriority.MEDIUM,
    )

    status = Column(
        Enum(IssueStatus),
        nullable=False,
        default=IssueStatus.TODO,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    assignee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
    )

    reporter_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
    )

    due_date = Column(DateTime)

    completed_at = Column(
        DateTime(timezone=True), 
        nullable=True
    )

    project = relationship(
        "Project",
        back_populates="issues"
    )

    assignee = relationship(
        "Employee",
        foreign_keys=[assignee_id],
        back_populates="assigned_issues",
    )

    reporter = relationship(
        "Employee",
        foreign_keys=[reporter_id],
        back_populates="reported_issues",
    )

    comments = relationship(
        "Comment",
        back_populates="issue",
        # cascade="all, delete-orphan",
    )

    attachments = relationship(
        "Attachment",
        back_populates="issue",
        cascade="all, delete-orphan",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )