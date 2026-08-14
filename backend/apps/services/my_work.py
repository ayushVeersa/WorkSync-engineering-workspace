from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, status

from apps.models.user import User
from apps.models.employee import Employee
from apps.models.issue import Issue
from apps.schemas.issue import IssueStatus, IssuePriority, IssueType, IssueResponse
from apps.schemas.my_work import MyWorkResponse, WorkSummary
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_my_work_data(
    db: Session,
    user: User,
    status_filter: Optional[IssueStatus] = None,
    priority_filter: Optional[IssuePriority] = None,
    project_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> MyWorkResponse:
    """
    Fetch tasks assigned to current employee and compute work statistics.
    """
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()

    if not employee:
        logger.warning("No employee profile associated with user_id=%s", user.id)
        # Return empty stats & lists if user is not an employee profile yet
        return MyWorkResponse(
            summary=WorkSummary(
                assigned=0,
                in_progress=0,
                due_soon=0,
                overdue=0,
                completed=0,
            ),
            today=[],
            upcoming=[],
            overdue=[],
            recently_completed=[],
        )

    # Base query for all assigned tasks
    query = db.query(Issue).filter(Issue.assignee_id == employee.id)

    if status_filter:
        raw_st = str(status_filter).strip().upper()
        if raw_st in ("ALL", "ALL_STATUSES", "NULL", "NONE", "UNDEFINED", ""):
            status_filter = None

    if priority_filter:
        raw_pr = str(priority_filter).strip().upper()
        if raw_pr in ("ALL", "ALL_PRIORITIES", "NULL", "NONE", "UNDEFINED", ""):
            priority_filter = None

    if status_filter:
        query = query.filter(Issue.status == status_filter)

    if priority_filter:
        query = query.filter(Issue.priority == priority_filter)

    if project_id:
        query = query.filter(Issue.project_id == project_id)

    if search:
        query = query.filter(
            Issue.title.ilike(f"%{search}%") | Issue.description.ilike(f"%{search}%")
        )

    all_assigned_issues = query.all()

    now = datetime.now(timezone.utc)
    # Remove tzinfo for comparing with naive SQLite datetime objects
    now_naive = datetime.now()

    three_days_later = now_naive + timedelta(days=3)

    assigned_count = len(all_assigned_issues)
    in_progress_count = 0
    due_soon_count = 0
    overdue_count = 0
    completed_count = 0

    today_tasks = []
    upcoming_tasks = []
    overdue_tasks = []
    recently_completed_tasks = []

    for issue in all_assigned_issues:
        is_completed = issue.status == IssueStatus.DONE
        is_in_progress = issue.status == IssueStatus.IN_PROGRESS

        if is_completed:
            completed_count += 1
            recently_completed_tasks.append(issue)
            continue

        if is_in_progress:
            in_progress_count += 1

        due = issue.due_date
        if due:
            if due < now_naive:
                overdue_count += 1
                overdue_tasks.append(issue)
            elif due <= three_days_later:
                due_soon_count += 1
                today_tasks.append(issue)
            else:
                upcoming_tasks.append(issue)
        else:
            if is_in_progress or issue.status == IssueStatus.TODO:
                today_tasks.append(issue)

    summary = WorkSummary(
        assigned=assigned_count,
        in_progress=in_progress_count,
        due_soon=due_soon_count,
        overdue=overdue_count,
        completed=completed_count,
    )

    return MyWorkResponse(
        summary=summary,
        today=[IssueResponse.model_validate(i) for i in today_tasks[skip:skip+limit]],
        upcoming=[IssueResponse.model_validate(i) for i in upcoming_tasks[skip:skip+limit]],
        overdue=[IssueResponse.model_validate(i) for i in overdue_tasks[skip:skip+limit]],
        recently_completed=[IssueResponse.model_validate(i) for i in recently_completed_tasks[skip:skip+limit]],
    )
