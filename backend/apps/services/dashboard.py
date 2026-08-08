from sqlalchemy.orm import Session
from sqlalchemy import func

from apps.models.employee import Employee
from apps.models.department import Department
from apps.models.project import Project
from apps.models.issue import Issue
from apps.models.comment import Comment
from apps.models.employee_project import EmployeeProject
from apps.schemas.project import ProjectStatus
from apps.schemas.issue import (
    IssueStatus,
)
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_dashboard_summary(db: Session):

    summary = {
        "total_employees": db.query(func.count(Employee.id)).scalar(),

        "total_departments": db.query(func.count(Department.id)).scalar(),

        "total_projects": db.query(func.count(Project.id)).scalar(),

        "total_issues": db.query(func.count(Issue.id)).scalar(),

        "total_comments": db.query(func.count(Comment.id)).scalar(),

        "active_projects": (
            db.query(func.count(Project.id))
            .filter(Project.status == ProjectStatus.ACTIVE)
            .scalar()
        )
    }

    logger.info("Computed dashboard summary: %s", summary)
    return summary


def get_my_work(
    db: Session,
    employee_id: int,
):

    assigned = (
        db.query(func.count(Issue.id))
        .filter(Issue.assignee_id == employee_id)
        .scalar()
    )

    completed = (
        db.query(func.count(Issue.id))
        .filter(
            Issue.assignee_id == employee_id,
            Issue.status == IssueStatus.DONE,
        )
        .scalar()
    )

    projects = (
        db.query(func.count(EmployeeProject.project_id))
        .filter(EmployeeProject.employee_id == employee_id)
        .scalar()
    )

    comments = (
        db.query(func.count(Comment.id))
        .filter(Comment.employee_id == employee_id)
        .scalar()
    )

    result = {
        "assigned_issues": assigned,
        "completed_issues": completed,
        "projects": projects,
        "comments": comments,
    }
    logger.info("Computed my-work summary for employee_id=%s: %s", employee_id, result)
    return result


def issues_by_status(db: Session):

    rows = (
        db.query(
            Issue.status,
            func.count(Issue.id)
        )
        .group_by(Issue.status)
        .all()
    )

    result = [
        {
            "status": status.value,
            "count": count,
        }
        for status, count in rows
    ]
    logger.info("Computed issues-by-status: %s", result)
    return result


def issues_by_priority(db: Session):

    rows = (
        db.query(
            Issue.priority,
            func.count(Issue.id)
        )
        .group_by(Issue.priority)
        .all()
    )

    result = [
        {
            "priority": priority.value,
            "count": count,
        }
        for priority, count in rows
    ]
    logger.info("Computed issues-by-priority: %s", result)
    return result


def project_overview(db: Session):

    projects = db.query(Project).all()

    data = []

    for project in projects:

        members = (
            db.query(func.count(EmployeeProject.employee_id))
            .filter(EmployeeProject.project_id == project.id)
            .scalar()
        )

        issues = (
            db.query(func.count(Issue.id))
            .filter(Issue.project_id == project.id)
            .scalar()
        )

        data.append(
            {
                "id": project.id,
                "name": project.name,
                "members": members,
                "issues": issues,
            }
        )

    logger.info("Computed project overview for %s projects", len(data))
    return data
