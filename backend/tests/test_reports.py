import pytest
from datetime import datetime, timedelta

from apps.models.user import User
from apps.models.department import Department
from apps.models.employee import Employee
from apps.models.project import Project
from apps.models.issue import Issue
from apps.schemas.issue import IssueStatus, IssuePriority, IssueType
from apps.schemas.role import Role
from apps.services.reports import (
    get_task_overview,
    get_completion_trends,
    get_task_distribution,
    get_team_workload,
    get_cycle_time_report,
)


def test_reports_overview_and_distribution(db):
    dept = Department(name="Backend Eng", description="Backend")
    db.add(dept)
    db.commit()

    u = User(name="Tech Lead", email="lead@test.com", password_hash="hash", age=35, role=Role.MANAGER)
    db.add(u)
    db.commit()

    emp = Employee(user_id=u.id, department_id=dept.id, designation="Lead", age=35)
    db.add(emp)
    db.commit()

    proj = Project(name="API Core", owner_id=emp.id)
    db.add(proj)
    db.commit()

    i1 = Issue(
        title="Task 1",
        project_id=proj.id,
        assignee_id=emp.id,
        reporter_id=emp.id,
        status=IssueStatus.DONE,
        priority=IssuePriority.HIGH,
        issue_type=IssueType.STORY,
    )
    i2 = Issue(
        title="Task 2",
        project_id=proj.id,
        assignee_id=emp.id,
        reporter_id=emp.id,
        status=IssueStatus.IN_PROGRESS,
        priority=IssuePriority.MEDIUM,
        issue_type=IssueType.TASK,
    )
    db.add_all([i1, i2])
    db.commit()

    overview = get_task_overview(db, project_id=proj.id)
    assert overview.total_tasks == 2
    assert overview.completed == 1
    assert overview.in_progress == 1
    assert overview.completion_rate_percentage == 50.0

    dist = get_task_distribution(db, project_id=proj.id)
    assert len(dist.by_status) >= 2
    assert len(dist.by_priority) >= 2

    workload = get_team_workload(db, department_id=dept.id)
    assert len(workload.workload) == 1
    assert workload.workload[0].active_tasks == 1
    assert workload.workload[0].completed_tasks == 1

    cycle = get_cycle_time_report(db, project_id=proj.id)
    assert cycle.avg_cycle_time_days >= 0.0
