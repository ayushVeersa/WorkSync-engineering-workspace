"""
Tests for comment service functions and endpoints.
"""

import pytest
from fastapi import HTTPException

from apps.schemas.role import Role
from apps.services.comment import (
    get_comment,
    get_issue_comments,
    create_comment,
    update_comment,
    delete_comment,
)
from apps.schemas.comment import CommentCreate, CommentUpdate


# --------------------------- Service tests ---------------------------


def _setup(db, make_department, make_user, make_employee, make_project, assign, role=Role.ADMIN):
    admin = make_user(role=role, email="admin@test.com")
    reporter = make_employee(admin, make_department(name="CSE").id)
    other_user = make_user(email="assignee@test.com", role=Role.EMPLOYEE)
    assignee = make_employee(other_user, reporter.department_id)
    project = make_project("Project X", reporter.id)
    assign(assignee.id, project.id)
    assign(reporter.id, project.id)
    return admin, reporter, assignee, project


def _make_issue_and_ctx(db, make_department, make_user, make_employee, make_project, assign, role=Role.ADMIN):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign, role
    )
    issue = create_issue(
        db,
        IssueCreate(
            title="Issue",
            description="desc",
            project_id=project.id,
            assignee_id=assignee.id,
        ),
        reporter_id=reporter.id,
    )
    return admin, reporter, assignee, project, issue


def test_get_comment_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_comment(db, 999)
    assert exc.value.status_code == 404


def test_create_comment(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    comment = create_comment(
        db,
        issue.id,
        CommentCreate(content="This is now fixed."),
        employee_id=assignee.id,
    )
    assert comment.id
    assert comment.content == "This is now fixed."
    assert comment.issue_id == issue.id


def test_create_comment_issue_not_found(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    emp = make_employee(u1, dept.id)
    with pytest.raises(HTTPException) as exc:
        create_comment(db, 999, CommentCreate(content="hi"), employee_id=emp.id)
    assert exc.value.status_code == 404


def test_create_comment_not_member(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    outsider_user = make_user(email="outsider@test.com")
    outsider = make_employee(outsider_user, reporter.department_id)

    with pytest.raises(HTTPException) as exc:
        create_comment(
            db,
            issue.id,
            CommentCreate(content="hi"),
            employee_id=outsider.id,
        )
    assert exc.value.status_code == 403


def test_get_issue_comments(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    create_comment(db, issue.id, CommentCreate(content="c1"), employee_id=assignee.id)
    create_comment(db, issue.id, CommentCreate(content="c2"), employee_id=assignee.id)

    comments = get_issue_comments(db, issue.id)
    assert len(comments) == 2


def test_get_issue_comments_empty(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    assert get_issue_comments(db, issue.id) == []


def test_update_comment_own(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    comment = create_comment(db, issue.id, CommentCreate(content="original"), employee_id=assignee.id)
    updated = update_comment(db, comment.id, CommentUpdate(content="updated"), assignee)
    assert updated.content == "updated"


def test_update_comment_not_found(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    with pytest.raises(HTTPException) as exc:
        update_comment(db, 999, CommentUpdate(content="nope"), assignee)
    assert exc.value.status_code == 404


def test_update_comment_unauthorized(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    comment = create_comment(db, issue.id, CommentCreate(content="original"), employee_id=assignee.id)
    # another project member who is neither the author nor an admin
    other_user = make_user(email="other@test.com", role=Role.EMPLOYEE)
    other_member = make_employee(other_user, reporter.department_id)
    assign(other_member.id, project.id)

    with pytest.raises(HTTPException) as exc:
        update_comment(db, comment.id, CommentUpdate(content="hacked"), other_member)
    assert exc.value.status_code == 403


def test_update_comment_as_admin(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    comment = create_comment(db, issue.id, CommentCreate(content="original"), employee_id=assignee.id)
    updated = update_comment(db, comment.id, CommentUpdate(content="admin edit"), reporter)
    assert updated.content == "admin edit"


def test_delete_comment(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    comment = create_comment(db, issue.id, CommentCreate(content="to delete"), employee_id=assignee.id)
    result = delete_comment(db, comment.id, assignee)
    assert result["message"] == "Comment deleted successfully"
    assert get_issue_comments(db, issue.id) == []


def test_delete_comment_not_found(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    with pytest.raises(HTTPException) as exc:
        delete_comment(db, 999, assignee)
    assert exc.value.status_code == 404


def test_delete_comment_unauthorized(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, assignee, project, issue = _make_issue_and_ctx(
        db, make_department, make_user, make_employee, make_project, assign
    )
    comment = create_comment(db, issue.id, CommentCreate(content="to delete"), employee_id=assignee.id)
    # another project member who is neither the author nor an admin
    other_user = make_user(email="other@test.com", role=Role.EMPLOYEE)
    other_member = make_employee(other_user, reporter.department_id)
    assign(other_member.id, project.id)

    with pytest.raises(HTTPException) as exc:
        delete_comment(db, comment.id, other_member)
    assert exc.value.status_code == 403


# --------------------------- Endpoint tests ---------------------------


def test_comment_endpoints_flow(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    # create
    resp = client.post(
        f"/comments/issue/{issue.id}",
        headers=headers,
        json={"content": "This is now fixed."},
    )
    assert resp.status_code == 201
    comment = resp.json()
    assert comment["content"] == "This is now fixed."

    # list
    resp = client.get(f"/comments/issue/{issue.id}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # update (admin can update any)
    resp = client.put(
        f"/comments/{comment['id']}",
        headers=headers,
        json={"content": "Updated text"},
    )
    assert resp.status_code == 200
    assert resp.json()["content"] == "Updated text"

    # delete
    resp = client.delete(f"/comments/{comment['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Comment deleted successfully"


def test_comment_create_requires_membership(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    # outsider user not part of project
    outsider_user = make_user(role=Role.EMPLOYEE, email="outsider@test.com")
    make_employee(outsider_user, reporter.department_id)
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': outsider_user.email})}"}

    resp = client.post(
        f"/comments/issue/{issue.id}",
        headers=headers,
        json={"content": "hi"},
    )
    assert resp.status_code == 403


def test_comment_create_requires_employee(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    # user with no employee record
    no_emp_user = make_user(role=Role.EMPLOYEE, email="noemp@test.com")
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': no_emp_user.email})}"}

    resp = client.post(
        f"/comments/issue/{issue.id}",
        headers=headers,
        json={"content": "hi"},
    )
    assert resp.status_code == 404


def test_comment_update_unauthorized_endpoint(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    comment = create_comment(db, issue.id, CommentCreate(content="original"), employee_id=assignee.id)

    # a non-admin project member who is not the author
    other_user = make_user(email="other@test.com", role=Role.EMPLOYEE)
    other_member = make_employee(other_user, reporter.department_id)
    assign(other_member.id, project.id)
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': other_user.email})}"}

    resp = client.put(
        f"/comments/{comment.id}",
        headers=headers,
        json={"content": "hacked"},
    )
    assert resp.status_code == 403


def test_comment_delete_unauthorized_endpoint(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    comment = create_comment(db, issue.id, CommentCreate(content="to delete"), employee_id=assignee.id)

    # a non-admin project member who is not the author
    other_user = make_user(email="other@test.com", role=Role.EMPLOYEE)
    other_member = make_employee(other_user, reporter.department_id)
    assign(other_member.id, project.id)
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': other_user.email})}"}

    resp = client.delete(f"/comments/{comment.id}", headers=headers)
    assert resp.status_code == 403


def test_comment_update_not_found_endpoint(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    resp = client.put(
        "/comments/999",
        headers=headers,
        json={"content": "nope"},
    )
    assert resp.status_code == 404


def test_comment_delete_not_found_endpoint(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    resp = client.delete("/comments/999", headers=headers)
    assert resp.status_code == 404


def test_comment_endpoints_requires_auth(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue

    admin, reporter, assignee, project = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )

    # no auth header -> 401 from HTTPBearer
    resp = client.post(
        f"/comments/issue/{issue.id}",
        json={"content": "hi"},
    )
    assert resp.status_code == 401
