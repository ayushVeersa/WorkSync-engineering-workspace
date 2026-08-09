from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class IssueType(str, Enum):
    TASK = "TASK"
    BUG = "BUG"
    STORY = "STORY"


class IssuePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IssueStatus(str, Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    TESTING = "TESTING"
    DONE = "DONE"


class IssueCreate(BaseModel):
    title: str
    description: str | None = None
    issue_type: IssueType = IssueType.TASK
    priority: IssuePriority = IssuePriority.MEDIUM
    status: IssueStatus = IssueStatus.TODO
    assignee_id: int
    project_id: int
    due_date: datetime | None = None


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: IssuePriority | None = None
    status: IssueStatus | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None


class IssueResponse(BaseModel):
    id: int
    title: str
    description: str | None
    issue_type: IssueType = IssueType.TASK
    priority: IssuePriority = IssuePriority.MEDIUM
    status: IssueStatus = IssueStatus.TODO
    project_id: int
    assignee_id: int
    reporter_id: int
    due_date: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True
