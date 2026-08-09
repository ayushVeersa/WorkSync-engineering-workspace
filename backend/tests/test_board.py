"""
Tests for the Kanban board service and endpoint.
"""

import pytest
from fastapi import HTTPException

from apps.schemas.role import Role
from apps.schemas.issue import (
    IssueStatus,
    IssuePriority,
    IssueType,
)
from apps.services.board import get_project_board


def _setup_board(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="owner@test.com")
    u2 = make_user(email="assignee@test.com")
    owner = make_employee(u1, dept.id)
    assignee = make_employee(u2, dept.id)
    project = make_project("Board Project", owner.id)
    assign(assignee.id, project.id)

    make_issue(
        title="Task 1",
        project_id=project.id,
        assignee_id=assignee.id,
        reporter_id=owner.id,
        status=IssueStatus.TODO,
        priority=IssuePriority.HIGH,
        issue_type=IssueType.TASK,
    )
    make_issue(
        title="Bug 1",
        project_id=project.id,
        assignee_id=assignee.id,
        reporter_id=owner.id,
        status=IssueStatus.IN_PROGRESS,
        priority=IssuePriority.CRITICAL,
        issue_type=IssueType.BUG,
    )
    make_issue(
        title="Done 1",
        project_id=project.id,
        assignee_id=assignee.id,
        reporter_id=owner.id,
        status=IssueStatus.DONE,
        priority=IssuePriority.LOW,
        issue_type=IssueType.STORY,
    )
    return owner, assignee, project


# --------------------------- Service tests ---------------------------


def test_get_project_board_groups_by_status(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    _, _, project = _setup_board(
        db, make_department, make_user, make_employee, make_project, assign, make_issue
    )

    board = get_project_board(db, project.id)

    assert board.project_id == project.id
    assert board.project_name == "Board Project"

    # All statuses should be present as columns
    statuses = {col.status for col in board.columns}
    assert statuses == set(IssueStatus)

    # Verify issue placement
    by_status = {col.status: col.issues for col in board.columns}
    assert len(by_status[IssueStatus.TODO]) == 1
    assert by_status[IssueStatus.TODO][0].title == "Task 1"
    assert len(by_status[IssueStatus.IN_PROGRESS]) == 1
    assert by_status[IssueStatus.IN_PROGRESS][0].title == "Bug 1"
    assert len(by_status[IssueStatus.DONE]) == 1
    assert by_status[IssueStatus.DONE][0].title == "Done 1"

    # Empty columns should contain no issues
    assert len(by_status[IssueStatus.BACKLOG]) == 0
    assert len(by_status[IssueStatus.REVIEW]) == 0
    assert len(by_status[IssueStatus.TESTING]) == 0


def test_get_project_board_empty(db, make_department, make_user, make_employee, make_project):
    dept = make_department(name="CSE")
    u1 = make_user(email="owner@test.com")
    owner = make_employee(u1, dept.id)
    project = make_project("Empty Board", owner.id)

    board = get_project_board(db, project.id)

    assert board.project_id == project.id
    assert len(board.columns) == len(IssueStatus)
    for col in board.columns:
        assert col.issues == []


def test_get_project_board_project_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_project_board(db, 999)
    assert exc.value.status_code == 404


# --------------------------- Endpoint test ---------------------------


def test_board_endpoint(client, db, make_department, make_user, make_employee, make_project, assign, make_issue):
    from apps.services.jwt import create_access_token

    admin = make_user(role=Role.ADMIN, email="adminboard@test.com", name="Admin Board")
    dept = make_department(name="CSE")
    admin_emp = make_employee(admin, dept.id)
    project = make_project("Board Project", admin_emp.id)

    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    resp = client.get(f"/projects/{project.id}/board", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == project.id
    assert data["project_name"] == "Board Project"
    assert len(data["columns"]) == len(IssueStatus)


def test_board_endpoint_not_found(client, db, make_user_with_token):
    _, headers = make_user_with_token(role=Role.ADMIN)
    resp = client.get("/projects/999/board", headers=headers)
    assert resp.status_code == 404
