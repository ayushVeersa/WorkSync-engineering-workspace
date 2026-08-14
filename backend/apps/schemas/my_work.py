from pydantic import BaseModel
from typing import List, Optional
from apps.schemas.issue import IssueResponse


class WorkSummary(BaseModel):
    assigned: int = 0
    in_progress: int = 0
    due_soon: int = 0
    overdue: int = 0
    completed: int = 0


class MyWorkResponse(BaseModel):
    summary: WorkSummary
    today: List[IssueResponse] = []
    upcoming: List[IssueResponse] = []
    overdue: List[IssueResponse] = []
    recently_completed: List[IssueResponse] = []
