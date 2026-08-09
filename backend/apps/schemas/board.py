from pydantic import BaseModel

from apps.schemas.issue import IssueResponse


class BoardColumn(BaseModel):
    status: str
    issues: list[IssueResponse]


class BoardResponse(BaseModel):
    project_id: int
    project_name: str
    columns: list[BoardColumn]