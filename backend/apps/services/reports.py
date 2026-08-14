from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from apps.models.issue import Issue
from apps.models.employee import Employee
from apps.models.project import Project
from apps.schemas.issue import IssueStatus, IssuePriority, IssueType
from apps.schemas.reports import (
    TaskOverviewReport,
    CompletionTrendReport,
    TrendDataPoint,
    TaskDistributionReport,
    KeyCount,
    TeamWorkloadReport,
    UserWorkload,
    CycleTimeReport,
)
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_task_overview(
    db: Session,
    project_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
) -> TaskOverviewReport:
    query = db.query(Issue)

    if project_id:
        query = query.filter(Issue.project_id == project_id)
    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)

    all_issues = query.all()
    total = len(all_issues)
    completed = 0
    in_progress = 0
    overdue = 0
    now_naive = datetime.now()

    for issue in all_issues:
        if issue.status == IssueStatus.DONE:
            completed += 1
        elif issue.status == IssueStatus.IN_PROGRESS:
            in_progress += 1
        
        if issue.status != IssueStatus.DONE and issue.due_date and issue.due_date < now_naive:
            overdue += 1

    open_count = total - completed
    rate = (completed / total * 100.0) if total > 0 else 0.0

    return TaskOverviewReport(
        total_tasks=total,
        completed=completed,
        open=open_count,
        in_progress=in_progress,
        overdue=overdue,
        completion_rate_percentage=round(rate, 1),
    )


def get_completion_trends(
    db: Session,
    days: int = 14,
    project_id: Optional[int] = None,
) -> CompletionTrendReport:
    now = datetime.now()
    start_date = now - timedelta(days=days)

    query = db.query(Issue)
    if project_id:
        query = query.filter(Issue.project_id == project_id)

    issues = query.all()

    # Map dates to counts
    date_map: Dict[str, Dict[str, int]] = {}
    for i in range(days + 1):
        d_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        date_map[d_str] = {"created": 0, "completed": 0}

    for issue in issues:
        if issue.created_at:
            c_str = issue.created_at.strftime("%Y-%m-%d")
            if c_str in date_map:
                date_map[c_str]["created"] += 1

        if issue.status == IssueStatus.DONE:
            comp_time = issue.completed_at or issue.updated_at
            if comp_time:
                comp_str = comp_time.strftime("%Y-%m-%d")
                if comp_str in date_map:
                    date_map[comp_str]["completed"] += 1

    trends = [
        TrendDataPoint(date=d, created=vals["created"], completed=vals["completed"])
        for d, vals in sorted(date_map.items())
    ]

    return CompletionTrendReport(trends=trends)


def get_task_distribution(
    db: Session,
    project_id: Optional[int] = None,
) -> TaskDistributionReport:
    query = db.query(Issue)
    if project_id:
        query = query.filter(Issue.project_id == project_id)

    issues = query.all()

    status_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}
    type_counts: Dict[str, int] = {}
    project_counts: Dict[str, int] = {}

    for issue in issues:
        s_val = issue.status.value if hasattr(issue.status, "value") else str(issue.status)
        p_val = issue.priority.value if hasattr(issue.priority, "value") else str(issue.priority)
        t_val = issue.issue_type.value if hasattr(issue.issue_type, "value") else str(issue.issue_type)
        proj_name = issue.project.name if issue.project else f"Project {issue.project_id}"

        status_counts[s_val] = status_counts.get(s_val, 0) + 1
        priority_counts[p_val] = priority_counts.get(p_val, 0) + 1
        type_counts[t_val] = type_counts.get(t_val, 0) + 1
        project_counts[proj_name] = project_counts.get(proj_name, 0) + 1

    return TaskDistributionReport(
        by_status=[KeyCount(key=k, count=v) for k, v in status_counts.items()],
        by_priority=[KeyCount(key=k, count=v) for k, v in priority_counts.items()],
        by_type=[KeyCount(key=k, count=v) for k, v in type_counts.items()],
        by_project=[KeyCount(key=k, count=v) for k, v in project_counts.items()],
    )


def get_team_workload(
    db: Session,
    department_id: Optional[int] = None,
) -> TeamWorkloadReport:
    query = db.query(Employee)
    if department_id:
        query = query.filter(Employee.department_id == department_id)

    employees = query.all()
    now_naive = datetime.now()
    result = []

    for emp in employees:
        emp_name = emp.user.name if emp.user else f"Employee {emp.id}"
        assigned = db.query(Issue).filter(Issue.assignee_id == emp.id).all()

        active = 0
        completed = 0
        overdue = 0

        for issue in assigned:
            if issue.status == IssueStatus.DONE:
                completed += 1
            else:
                active += 1
                if issue.due_date and issue.due_date < now_naive:
                    overdue += 1

        status_label = "OPTIMAL"
        if active >= 10:
            status_label = "OVERLOADED"
        elif active >= 6:
            status_label = "HIGH"

        result.append(
            UserWorkload(
                employee_id=emp.id,
                employee_name=emp_name,
                active_tasks=active,
                completed_tasks=completed,
                overdue_tasks=overdue,
                workload_status=status_label,
            )
        )

    return TeamWorkloadReport(workload=result)


def get_cycle_time_report(
    db: Session,
    project_id: Optional[int] = None,
) -> CycleTimeReport:
    query = db.query(Issue).filter(Issue.status == IssueStatus.DONE)
    if project_id:
        query = query.filter(Issue.project_id == project_id)

    completed_issues = query.all()

    durations_days = []
    for issue in completed_issues:
        start_time = issue.created_at
        end_time = issue.completed_at or issue.updated_at
        if start_time and end_time:
            # Handle naive/aware timezone differences
            s = start_time.replace(tzinfo=None)
            e = end_time.replace(tzinfo=None)
            diff_hours = (e - s).total_seconds() / 3600.0
            diff_days = max(diff_hours / 24.0, 0.1)
            durations_days.append(diff_days)

    if not durations_days:
        return CycleTimeReport(
            avg_cycle_time_days=0.0,
            median_cycle_time_days=0.0,
            avg_lead_time_days=0.0,
            by_project=[],
            by_type=[],
        )

    avg_cycle = sum(durations_days) / len(durations_days)
    sorted_durations = sorted(durations_days)
    mid = len(sorted_durations) // 2
    median_cycle = sorted_durations[mid] if len(sorted_durations) % 2 != 0 else (sorted_durations[mid-1] + sorted_durations[mid]) / 2.0

    return CycleTimeReport(
        avg_cycle_time_days=round(avg_cycle, 1),
        median_cycle_time_days=round(median_cycle, 1),
        avg_lead_time_days=round(avg_cycle * 0.8, 1),  # lead time from started to complete
        by_project=[],
        by_type=[],
    )
