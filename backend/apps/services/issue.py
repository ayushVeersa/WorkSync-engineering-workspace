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
from apps.core.logging import get_logger

logger = get_logger(__name__)


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
        logger.warning("Issue not found for id=%s", issue_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    logger.info("Fetched issue id=%s", issue_id)
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

    issues = query.all()
    logger.info("Fetched all issues, count=%s, status=%s, priority=%s", len(issues), status, priority)
    return issues


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
        logger.warning("Project not found for id=%s while creating issue", issue.project_id)
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
        logger.warning("Employee not found for id=%s while creating issue", issue.assignee_id)
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
        logger.warning(
            "Employee %s not assigned to project %s while creating issue",
            issue.assignee_id,
            issue.project_id,
        )
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

    logger.info("Created issue id=%s title=%s project_id=%s reporter_id=%s",
                db_issue.id, db_issue.title, issue.project_id, reporter_id)
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

    logger.info("Updated issue id=%s with fields=%s", issue_id, list(data.keys()))
    return issue


def delete_issue(
    db: Session,
    issue_id: int,
):
    issue = get_issue(db, issue_id)

    db.delete(issue)
    db.commit()

    logger.info("Deleted issue id=%s", issue_id)
    return {
        "message": "Issue deleted successfully"
    }


def get_project_issues(
    db: Session,
    project_id: int,
):
    issues = (
        db.query(Issue)
        .filter(Issue.project_id == project_id)
        .all()
    )
    logger.info("Fetched issues for project_id=%s, count=%s", project_id, len(issues))
    return issues


def get_my_issues(
    db: Session,
    employee_id: int,
):
    issues = (
        db.query(Issue)
        .filter(Issue.assignee_id == employee_id)
        .all()
    )
    logger.info("Fetched my issues for employee_id=%s, count=%s", employee_id, len(issues))
    return issues


def get_issues_by_status(
    db: Session,
    status,
):
    issues = (
        db.query(Issue)
        .filter(Issue.status == status)
        .all()
    )
    logger.info("Fetched issues by status=%s, count=%s", status, len(issues))
    return issues


def get_issues_by_priority(
    db: Session,
    priority,
):
    issues = (
        db.query(Issue)
        .filter(Issue.priority == priority)
        .all()
    )
    logger.info("Fetched issues by priority=%s, count=%s", priority, len(issues))
    return issues
