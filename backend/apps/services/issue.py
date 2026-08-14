from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status as http_status, UploadFile, File, Depends
import uuid
from pathlib import Path

from apps.models.user import User
from apps.models.issue import Issue
from apps.models.project import Project
from apps.models.employee import Employee
from apps.models.attachment import Attachment
from apps.models.employee_project import EmployeeProject
from apps.schemas.role import Role
from apps.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueStatus,
    IssuePriority,
    IssueType,
)
from apps.core.logging import get_logger

logger = get_logger(__name__)

UPLOAD_DIR = Path("uploads/issues")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    logger.info("Fetched issue id=%s", issue_id)
    return issue


def get_all_issues(
    db: Session,
    user: User | None = None,
    status: IssueStatus | str | None = None,
    priority: IssuePriority | str | None = None,
    issue_type: IssueType | str | None = None,
    assignee_id: int | None = None,
    project_id: int | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
):

    query = db.query(Issue)

    if user and user.role == Role.EMPLOYEE:
        employee = (
            db.query(Employee)
            .filter(Employee.user_id == user.id)
            .first()
        )

        if not employee:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Employee profile not found",
            )

        query = db.query(Issue).filter(Issue.assignee_id == employee.id)

    if status is not None:
        raw_st = str(status).strip().upper()
        if raw_st in ("ALL", "ALL_STATUSES", "NULL", "NONE", "UNDEFINED", ""):
            status = None

    if priority is not None:
        raw_pr = str(priority).strip().upper()
        if raw_pr in ("ALL", "ALL_PRIORITIES", "NULL", "NONE", "UNDEFINED", ""):
            priority = None

    if issue_type is not None:
        raw_tp = str(issue_type).strip().upper()
        if raw_tp in ("ALL", "ALL_TYPES", "NULL", "NONE", "UNDEFINED", ""):
            issue_type = None

    if status is not None:
        query = query.filter(Issue.status == status)

    if priority is not None:
        query = query.filter(Issue.priority == priority)

    if issue_type is not None:
        query = query.filter(Issue.issue_type == issue_type)

    if assignee_id is not None:
        query = query.filter(Issue.assignee_id == assignee_id)

    if project_id is not None:
        query = query.filter(Issue.project_id == project_id)

    if search:
        query = query.filter(
            Issue.title.ilike(f"%{search}%")
            | Issue.description.ilike(f"%{search}%")
        )

    issues = query.offset(skip).limit(limit).all()
    logger.info(
        "Fetched all issues, count=%s, status=%s, priority=%s, issue_type=%s, "
        "assignee_id=%s, project_id=%s, search=%s, skip=%s, limit=%s",
        len(issues),
        status,
        priority,
        issue_type,
        assignee_id,
        project_id,
        search,
        skip,
        limit,
    )
    return issues


def create_issue(
    db: Session,
    issue: IssueCreate,
    reporter_id: int,
    files: list[UploadFile] | None = None,
):
    project = (
        db.query(Project)
        .filter(Project.id == issue.project_id)
        .first()
    )

    if not project:
        logger.warning(
            "Project not found for id=%s while creating issue",
            issue.project_id,
        )
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    assignee = (
        db.query(Employee)
        .filter(Employee.id == issue.assignee_id)
        .first()
    )

    if not assignee:
        logger.warning(
            "Employee not found for id=%s while creating issue",
            issue.assignee_id,
        )
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
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
            status_code=http_status.HTTP_400_BAD_REQUEST,
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
    db.flush()

    if files:
        for file in files:
            if not file.filename:
                continue

            extension = Path(file.filename).suffix
            stored_name = f"{uuid.uuid4()}{extension}"
            file_path = UPLOAD_DIR / stored_name

            contents = file.file.read()

            with open(file_path, "wb") as buffer:
                buffer.write(contents)

            attachment = Attachment(
                original_name=file.filename,
                stored_name=stored_name,
                file_path=str(file_path),
                content_type=file.content_type or "application/octet-stream",
                file_size=len(contents),
                issue_id=db_issue.id,
                uploaded_by=reporter_id,
            )

            db.add(attachment)

    if db_issue.status == IssueStatus.DONE:
        db_issue.completed_at = func.now()

    db.commit()
    db.refresh(db_issue)

    logger.info(
        "Created issue id=%s title=%s project_id=%s reporter_id=%s",
        db_issue.id,
        db_issue.title,
        issue.project_id,
        reporter_id,
    )

    try:
        from apps.services.activity import record_activity
        record_activity(
            db=db,
            action="TASK_CREATED",
            entity_type="issue",
            entity_id=db_issue.id,
            actor_id=reporter_id,
            metadata={"title": db_issue.title, "status": str(db_issue.status)},
        )
    except Exception as exc:
        logger.warning("Could not record activity for task creation: %s", exc)

    return db_issue


def update_issue(
    db: Session,
    issue_id: int,
    payload: IssueUpdate,
):
    issue = get_issue(db, issue_id)

    data = payload.model_dump(exclude_unset=True)
    old_status = issue.status
    old_priority = issue.priority
    old_assignee = issue.assignee_id

    for key, value in data.items():
        setattr(issue, key, value)

    if "status" in data:
        if issue.status == IssueStatus.DONE and old_status != IssueStatus.DONE:
            issue.completed_at = func.now()
        elif issue.status != IssueStatus.DONE and old_status == IssueStatus.DONE:
            issue.completed_at = None

    db.commit()
    db.refresh(issue)

    logger.info("Updated issue id=%s with fields=%s", issue_id, list(data.keys()))

    try:
        from apps.services.activity import record_activity
        if "status" in data and old_status != issue.status:
            record_activity(
                db=db,
                action="TASK_STATUS_CHANGED",
                entity_type="issue",
                entity_id=issue.id,
                actor_id=issue.assignee_id,
                metadata={"old_status": str(old_status), "new_status": str(issue.status)},
            )
        if "priority" in data and old_priority != issue.priority:
            record_activity(
                db=db,
                action="TASK_PRIORITY_CHANGED",
                entity_type="issue",
                entity_id=issue.id,
                actor_id=issue.assignee_id,
                metadata={"old_priority": str(old_priority), "new_priority": str(issue.priority)},
            )
        if "assignee_id" in data and old_assignee != issue.assignee_id:
            record_activity(
                db=db,
                action="TASK_ASSIGNED",
                entity_type="issue",
                entity_id=issue.id,
                actor_id=issue.assignee_id,
                metadata={"old_assignee_id": old_assignee, "new_assignee_id": issue.assignee_id},
            )
    except Exception as exc:
        logger.warning("Could not record activity for task update: %s", exc)

    return issue


def delete_issue(
    db: Session,
    issue_id: int,
):
    issue = get_issue(db, issue_id)

    db.delete(issue)
    db.commit()

    logger.info("Deleted issue id=%s", issue_id)
    try:
        from apps.services.activity import record_activity
        record_activity(
            db=db,
            action="TASK_DELETED",
            entity_type="issue",
            entity_id=issue_id,
            actor_id=issue.assignee_id,
        )
    except Exception as exc:
        logger.warning("Could not record activity for task deletion: %s", exc)

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
