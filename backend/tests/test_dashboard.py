"""
Tests for dashboard service functions and endpoints.
"""

import pytest

from apps.schemas.role import Role
from apps.schemas.project import ProjectStatus
from apps.schemas.issue import IssueStatus, IssuePriority
from apps.services.dashboard import (
    get_dashboard_summary,
    get_my_work,
    issues_by_status,
    issues_by_priority,
    project_overview,
)


def _setup_data(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com", role=Role.ADMIN)
    u2 = make_user(email="b@test.com", role=Role.EMPLOYEE)
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    p1 = make_project("Project A", emp1.id, status=ProjectStatus.ACTIVE)
    p2 = make_project("Project B", emp1.id, status=ProjectStatus.PLANNING)

    assign(emp2.id, p1.id)
    assign(emp2.id, p2.id)

    make_issue(
        title="I1", project_id=p1.id, assignee_id=emp2.id, reporter_id=emp1.id,
        status=IssueStatus.DONE, priority=IssuePriority.HIGH,
    )
    make_issue(
        title="I2", project_id=p1.id, assignee_id=emp2.id, reporter_id=emp1.id,
        status=IssueStatus.IN_PROGRESS, priority=IssuePriority.LOW,
    )
    return u1, emp1, emp2, p1, p2


# --------------------------- Service tests ---------------------------


def test_get_dashboard_summary(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    _setup_data(db, make_department, make_user, make_employee, make_project, assign, make_issue)
    summary = get_dashboard_summary(db)
    assert summary["total_employees"] == 2
    assert summary["total_departments"] == 1
    assert summary["total_projects"] == 2
    assert summary["total_issues"] == 2
    assert summary["total_comments"] == 0
    assert summary["active_projects"] == 1


def test_get_my_work(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept, emp1, emp2, p1, p2 = _setup_data(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )
    work = get_my_work(db, emp2.id)
    assert work["assigned_issues"] == 2
    assert work["completed_issues"] == 1
    assert work["projects"] == 2
    assert work["comments"] == 0


def test_issues_by_status(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    _setup_data(db, make_department, make_user, make_employee, make_project, assign, make_issue)
    result = issues_by_status(db)
    by_status = {r["status"]: r["count"] for r in result}
    assert by_status[IssueStatus.DONE.value] == 1
    assert by_status[IssueStatus.IN_PROGRESS.value] == 1


def test_issues_by_priority(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    _setup_data(db, make_department, make_user, make_employee, make_project, assign, make_issue)
    result = issues_by_priority(db)
    by_priority = {r["priority"]: r["count"] for r in result}
    assert by_priority[IssuePriority.HIGH.value] == 1
    assert by_priority[IssuePriority.LOW.value] == 1


def test_project_overview(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept, emp1, emp2, p1, p2 = _setup_data(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )
    overview = project_overview(db)
    by_id = {p["id"]: p for p in overview}
    assert by_id[p1.id]["members"] == 1
    assert by_id[p1.id]["issues"] == 2
    assert by_id[p2.id]["members"] == 1


# --------------------------- Endpoint tests ---------------------------


def test_dashboard_summary_endpoint(client, db, make_department, make_user, make_employee, make_project, assign, make_issue):
    from apps.services.jwt import create_access_token

    admin, emp1, emp2, p1, p2 = _setup_data(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    resp = client.get("/dashboard/summary", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_employees"] == 2
    assert data["total_projects"] == 2


def test_dashboard_my_work_endpoint(client, db, make_department, make_user, make_employee, make_project, assign, make_issue):
    from apps.services.jwt import create_access_token

    admin, emp1, emp2, p1, p2 = _setup_data(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    resp = client.get("/dashboard/my-work", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["assigned_issues"] == 0  # admin has no assigned issues


def test_dashboard_status_endpoint(client, db, make_department, make_user, make_employee, make_project, assign, make_issue):
    from apps.services.jwt import create_access_token

    admin, emp1, emp2, p1, p2 = _setup_data(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}
    resp = client.get("/dashboard/issues/status", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_dashboard_priority_endpoint(client, db, make_department, make_user, make_employee, make_project, assign, make_issue):
    from apps.services.jwt import create_access_token

    admin, emp1, emp2, p1, p2 = _setup_data(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}
    resp = client.get("/dashboard/issues/priority", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_dashboard_projects_endpoint(client, db, make_department, make_user, make_employee, make_project, assign, make_issue):
    from apps.services.jwt import create_access_token

    admin, emp1, emp2, p1, p2 = _setup_data(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}
    resp = client.get("/dashboard/projects", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_dashboard_requires_auth(client):
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 401
