"""
Tests for issue service functions and endpoints.
"""

import pytest
from fastapi import HTTPException

from apps.schemas.role import Role
from apps.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueStatus,
    IssuePriority,
    IssueType,
)
from apps.services.issue import (
    get_issue,
    get_all_issues,
    create_issue,
    update_issue,
    delete_issue,
    get_project_issues,
    get_my_issues,
    get_issues_by_status,
    get_issues_by_priority,
)


def issue_payload(**kw):
    payload = {
        "title": "Fix login bug",
        "description": "Users cannot log in",
        "issue_type": "BUG",
        "priority": "HIGH",
        "status": "IN_PROGRESS",
        "assignee_id": 2,
        "project_id": 1,
    }
    payload.update(kw)
    return payload


# --------------------------- Service tests ---------------------------


def test_get_issue_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_issue(db, 999)
    assert exc.value.status_code == 404


def test_create_issue(db, make_department, make_user, make_employee, make_project, assign):
    dept = make_department(name="CSE")
    u1 = make_user(email="reporter@test.com")
    u2 = make_user(email="assignee@test.com")
    reporter = make_employee(u1, dept.id)
    assignee = make_employee(u2, dept.id)
    project = make_project("Project A", reporter.id)
    assign(assignee.id, project.id)

    issue = create_issue(
        db,
        IssueCreate(**issue_payload(assignee_id=assignee.id, project_id=project.id)),
        reporter_id=reporter.id,
    )
    assert issue.id
    assert issue.title == "Fix login bug"
    assert issue.reporter_id == reporter.id


def test_create_issue_project_not_found(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    u1 = make_user(email="reporter@test.com")
    u2 = make_user(email="assignee@test.com")
    reporter = make_employee(u1, dept.id)
    assignee = make_employee(u2, dept.id)

    with pytest.raises(HTTPException) as exc:
        create_issue(
            db,
            IssueCreate(**issue_payload(assignee_id=assignee.id, project_id=999)),
            reporter_id=reporter.id,
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == "Project not found"


def test_create_issue_assignee_not_found(db, make_department, make_user, make_employee, make_project, assign):
    dept = make_department(name="CSE")
    u1 = make_user(email="reporter@test.com")
    reporter = make_employee(u1, dept.id)
    project = make_project("Project A", reporter.id)

    with pytest.raises(HTTPException) as exc:
        create_issue(
            db,
            IssueCreate(**issue_payload(assignee_id=999, project_id=project.id)),
            reporter_id=reporter.id,
        )
    assert exc.value.status_code == 404


def test_create_issue_assignee_not_assigned(db, make_department, make_user, make_employee, make_project):
    dept = make_department(name="CSE")
    u1 = make_user(email="reporter@test.com")
    u2 = make_user(email="assignee@test.com")
    reporter = make_employee(u1, dept.id)
    assignee = make_employee(u2, dept.id)
    project = make_project("Project A", reporter.id)

    with pytest.raises(HTTPException) as exc:
        create_issue(
            db,
            IssueCreate(**issue_payload(assignee_id=assignee.id, project_id=project.id)),
            reporter_id=reporter.id,
        )
    assert exc.value.status_code == 400


def test_get_all_issues_filters(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)

    make_issue(
        title="Bug",
        project_id=project.id,
        assignee_id=emp2.id,
        reporter_id=emp1.id,
        status=IssueStatus.IN_PROGRESS,
        priority=IssuePriority.HIGH,
        issue_type=IssueType.BUG,
    )
    make_issue(
        title="Task",
        project_id=project.id,
        assignee_id=emp2.id,
        reporter_id=emp1.id,
        status=IssueStatus.TODO,
        priority=IssuePriority.LOW,
        issue_type=IssueType.TASK,
    )

    assert len(get_all_issues(db)) == 2
    assert len(get_all_issues(db, status=IssueStatus.IN_PROGRESS)) == 1
    assert len(get_all_issues(db, priority=IssuePriority.LOW)) == 1
    assert len(get_all_issues(db, status=IssueStatus.DONE)) == 0


def test_get_all_issues_search_and_filters(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)

    make_issue(
        title="Login Bug",
        project_id=project.id,
        assignee_id=emp2.id,
        reporter_id=emp1.id,
        status=IssueStatus.IN_PROGRESS,
        priority=IssuePriority.HIGH,
        issue_type=IssueType.BUG,
    )
    make_issue(
        title="Payment Task",
        project_id=project.id,
        assignee_id=emp2.id,
        reporter_id=emp1.id,
        status=IssueStatus.TODO,
        priority=IssuePriority.LOW,
        issue_type=IssueType.TASK,
    )
    make_issue(
        title="Auth Story",
        project_id=project.id,
        assignee_id=emp2.id,
        reporter_id=emp1.id,
        status=IssueStatus.DONE,
        priority=IssuePriority.MEDIUM,
        issue_type=IssueType.STORY,
    )

    # search by title
    assert len(get_all_issues(db, search="log")) == 1
    assert get_all_issues(db, search="log")[0].title == "Login Bug"

    # search by description (default "Issue description" for all created issues)
    assert len(get_all_issues(db, search="issue description")) == 3

    # filter by issue_type
    assert len(get_all_issues(db, issue_type=IssueType.BUG)) == 1
    assert len(get_all_issues(db, issue_type=IssueType.TASK)) == 1
    assert len(get_all_issues(db, issue_type=IssueType.STORY)) == 1

    # filter by assignee
    assert len(get_all_issues(db, assignee_id=emp2.id)) == 3
    assert len(get_all_issues(db, assignee_id=999)) == 0

    # combined filters
    assert len(get_all_issues(db, status=IssueStatus.DONE, issue_type=IssueType.STORY)) == 1
    assert len(get_all_issues(db, status=IssueStatus.DONE, issue_type=IssueType.BUG)) == 0

    # pagination
    assert len(get_all_issues(db, skip=0, limit=2)) == 2
    assert len(get_all_issues(db, skip=2, limit=2)) == 1


def test_get_project_issues(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    p1 = make_project("Project A", emp1.id)
    p2 = make_project("Project B", emp1.id)
    assign(emp2.id, p1.id)
    assign(emp2.id, p2.id)

    make_issue(title="I1", project_id=p1.id, assignee_id=emp2.id, reporter_id=emp1.id)
    make_issue(title="I2", project_id=p1.id, assignee_id=emp2.id, reporter_id=emp1.id)
    make_issue(title="I3", project_id=p2.id, assignee_id=emp2.id, reporter_id=emp1.id)

    assert len(get_project_issues(db, p1.id)) == 2
    assert len(get_project_issues(db, p2.id)) == 1


def test_get_my_issues(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)

    make_issue(title="I1", project_id=project.id, assignee_id=emp2.id, reporter_id=emp1.id)
    make_issue(title="I2", project_id=project.id, assignee_id=emp2.id, reporter_id=emp1.id)

    assert len(get_my_issues(db, emp2.id)) == 2
    assert len(get_my_issues(db, emp1.id)) == 0


def test_get_issues_by_status_and_priority(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)

    make_issue(title="I1", project_id=project.id, assignee_id=emp2.id, reporter_id=emp1.id,
               status=IssueStatus.DONE, priority=IssuePriority.HIGH)

    assert len(get_issues_by_status(db, IssueStatus.DONE)) == 1
    assert len(get_issues_by_status(db, IssueStatus.TODO)) == 0
    assert len(get_issues_by_priority(db, IssuePriority.HIGH)) == 1
    assert len(get_issues_by_priority(db, IssuePriority.LOW)) == 0


def test_update_issue(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)
    issue = make_issue(title="I1", project_id=project.id, assignee_id=emp2.id, reporter_id=emp1.id)

    updated = update_issue(db, issue.id, IssueUpdate(status=IssueStatus.DONE))
    assert updated.status == IssueStatus.DONE


def test_delete_issue(db, make_department, make_user, make_employee, make_project, assign, make_issue):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)
    issue = make_issue(title="I1", project_id=project.id, assignee_id=emp2.id, reporter_id=emp1.id)

    result = delete_issue(db, issue.id)
    assert result["message"] == "Issue deleted successfully"
    assert get_all_issues(db) == []


# --------------------------- Endpoint tests ---------------------------


def _setup_issue_ctx(db, make_department, make_user, make_employee, make_project, assign, role=Role.ADMIN):
    admin = make_user(role=role, email="admin@test.com")
    reporter = make_employee(admin, make_department(name="CSE").id)
    other_user = make_user(email="assignee@test.com", role=Role.EMPLOYEE)
    assignee = make_employee(other_user, reporter.department_id)
    project = make_project("Project X", reporter.id)
    assign(assignee.id, project.id)
    return admin, reporter, assignee, project


def test_issue_endpoints_flow(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup_issue_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    # create
    resp = client.post(
        "/issues",
        headers=headers,
        json=issue_payload(assignee_id=assignee.id, project_id=project.id),
    )
    assert resp.status_code == 201
    issue = resp.json()
    assert issue["title"] == "Fix login bug"

    # list
    resp = client.get("/issues", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # filter
    resp = client.get("/issues?status=IN_PROGRESS&priority=HIGH", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # me
    resp = client.get("/issues/me", headers=headers)
    assert resp.status_code == 200

    # project issues
    resp = client.get(f"/issues/project/{project.id}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # get by id
    resp = client.get(f"/issues/{issue['id']}", headers=headers)
    assert resp.status_code == 200

    # update
    resp = client.put(
        f"/issues/{issue['id']}",
        headers=headers,
        json={"status": "DONE"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "DONE"

    # delete
    resp = client.delete(f"/issues/{issue['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Issue deleted successfully"


def test_issue_create_unauthorized_assignee(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup_issue_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    # Create a user NOT assigned to the project
    outsider_user = make_user(email="outsider@test.com")
    make_employee(outsider_user, reporter.department_id)

    resp = client.post(
        "/issues",
        headers=headers,
        json=issue_payload(assignee_id=outsider_user.id, project_id=project.id),
    )
    # The assignee employee id is used; use valid employee but not assigned
    # Rebuild with the assignee's actual employee id but not assigned
    # Here outsider_user has no employee in project, but create_issue checks Employee existence first.
    # Since outsider has an employee record, it proceeds to assignment check -> 400
    assert resp.status_code == 400


def test_issue_not_found(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup_issue_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}
    resp = client.get("/issues/999", headers=headers)
    assert resp.status_code == 404
