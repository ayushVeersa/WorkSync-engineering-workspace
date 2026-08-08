from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.issue import Issue
from apps.models.project import Project
from apps.models.employee import Employee
from apps.models.employee_project import EmployeeProject
from apps.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueStatus,
    IssuePriority
)


def get_issue(
    db: Session,
    issue_id: int,
):
    issue = (
        db.query(Issue)
        .filter(Issue.id == issue_id)
        .first()
    )

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return issue


def get_all_issues(
    db: Session,
    status: IssueStatus | None = None,
    priority: IssuePriority | None = None,
):
    query = db.query(Issue)

    if status is not None:
        query = query.filter(Issue.status == status)

    if priority is not None:
        query = query.filter(Issue.priority == priority)

    return query.all()


def create_issue(
    db: Session,
    issue: IssueCreate,
    reporter_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == issue.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    assignee = (
        db.query(Employee)
        .filter(Employee.id == issue.assignee_id)
        .first()
    )

    if not assignee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    assignment = (
        db.query(EmployeeProject)
        .filter(
            EmployeeProject.employee_id == issue.assignee_id,
            EmployeeProject.project_id == issue.project_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=400,
            detail="Employee is not assigned to this project",
        )

    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        issue_type=issue.issue_type,
        priority=issue.priority,
        status=issue.status,
        project_id=issue.project_id,
        assignee_id=issue.assignee_id,
        reporter_id=reporter_id,
        due_date=issue.due_date,
    )

    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    return db_issue


def update_issue(
    db: Session,
    issue_id: int,
    payload: IssueUpdate,
):
    issue = get_issue(db, issue_id)

    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(issue, key, value)

    db.commit()
    db.refresh(issue)

    return issue


def delete_issue(
    db: Session,
    issue_id: int,
):
    issue = get_issue(db, issue_id)

    db.delete(issue)
    db.commit()

    return {
        "message": "Issue deleted successfully"
    }


def get_project_issues(
    db: Session,
    project_id: int,
):
    return (
        db.query(Issue)
        .filter(Issue.project_id == project_id)
        .all()
    )


def get_my_issues(
    db: Session,
    employee_id: int,
):
    return (
        db.query(Issue)
        .filter(Issue.assignee_id == employee_id)
        .all()
    )


def get_issues_by_status(
    db: Session,
    status,
):
    return (
        db.query(Issue)
        .filter(Issue.status == status)
        .all()
    )


def get_issues_by_priority(
    db: Session,
    priority,
):
    return (
        db.query(Issue)
        .filter(Issue.priority == priority)
        .all()
    )