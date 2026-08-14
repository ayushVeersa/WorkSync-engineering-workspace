import pytest
from datetime import datetime, timedelta

from apps.models.user import User
from apps.models.department import Department
from apps.models.employee import Employee
from apps.models.project import Project
from apps.models.issue import Issue
from apps.models.employee_project import EmployeeProject
from apps.schemas.issue import IssueStatus, IssuePriority, IssueType
from apps.schemas.role import Role
from apps.services.my_work import get_my_work_data


def test_my_work_empty(db):
    user = User(
        name="Test Employee",
        email="emp_mywork@test.com",
        password_hash="hash",
        age=25,
        role=Role.EMPLOYEE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    res = get_my_work_data(db, user)
    assert res.summary.assigned == 0
    assert res.summary.completed == 0
    assert res.today == []


def test_my_work_summary_and_sections(db):
    dept = Department(name="Eng", description="Eng")
    db.add(dept)
    db.commit()

    u = User(
        name="John Dev",
        email="johndev@test.com",
        password_hash="hash",
        age=28,
        role=Role.EMPLOYEE,
    )
    db.add(u)
    db.commit()

    emp = Employee(user_id=u.id, department_id=dept.id, designation="Dev", age=28)
    db.add(emp)
    db.commit()

    proj = Project(name="Project X", owner_id=emp.id)
    db.add(proj)
    db.commit()

    now = datetime.now()

    # Overdue task
    i1 = Issue(
        title="Overdue Task",
        project_id=proj.id,
        assignee_id=emp.id,
        reporter_id=emp.id,
        status=IssueStatus.TODO,
        priority=IssuePriority.HIGH,
        due_date=now - timedelta(days=2),
    )

    # In Progress Today
    i2 = Issue(
        title="In Progress Task",
        project_id=proj.id,
        assignee_id=emp.id,
        reporter_id=emp.id,
        status=IssueStatus.IN_PROGRESS,
        priority=IssuePriority.MEDIUM,
        due_date=now + timedelta(days=1),
    )

    # Completed Task
    i3 = Issue(
        title="Done Task",
        project_id=proj.id,
        assignee_id=emp.id,
        reporter_id=emp.id,
        status=IssueStatus.DONE,
        priority=IssuePriority.LOW,
    )

    db.add_all([i1, i2, i3])
    db.commit()

    res = get_my_work_data(db, u)

    assert res.summary.assigned == 3
    assert res.summary.in_progress == 1
    assert res.summary.overdue == 1
    assert res.summary.completed == 1

    assert len(res.overdue) == 1
    assert res.overdue[0].title == "Overdue Task"

    assert len(res.recently_completed) == 1
    assert res.recently_completed[0].title == "Done Task"
