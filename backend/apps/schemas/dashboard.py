from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_employees: int
    total_departments: int
    total_projects: int
    total_issues: int
    total_comments: int
    active_projects: int


class MyWorkSummary(BaseModel):
    assigned_issues: int
    completed_issues: int
    projects: int
    comments: int


class IssueStatusSummary(BaseModel):
    status: str
    count: int


class IssuePrioritySummary(BaseModel):
    priority: str
    count: int


class ProjectOverview(BaseModel):
    id: int
    name: str
    members: int
    issues: int