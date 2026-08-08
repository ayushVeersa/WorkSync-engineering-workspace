"""
Tests for attachment service functions and endpoints.
"""

import io
import os
import pytest
from fastapi import HTTPException
from fastapi.datastructures import UploadFile

from apps.services.attachment import (
    upload_attachment,
    get_issue_attachments,
    delete_attachment,
)
from apps.services import attachment as attachment_service


def _make_upload_file(name="screenshot.png", content=b"fake-image-data", content_type="image/png"):
    return UploadFile(
        filename=name,
        file=io.BytesIO(content),
        headers={"content-type": content_type},
    )


def _setup(db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue

    admin = make_user(role="ADMIN", email="admin@test.com")
    reporter = make_employee(admin, make_department(name="CSE").id)
    other_user = make_user(email="assignee@test.com", role="EMPLOYEE")
    assignee = make_employee(other_user, reporter.department_id)
    project = make_project("Project X", reporter.id)
    assign(assignee.id, project.id)
    issue = create_issue(
        db,
        IssueCreate(title="Issue", project_id=project.id, assignee_id=assignee.id),
        reporter_id=reporter.id,
    )
    return admin, reporter, issue


# --------------------------- Service tests ---------------------------


def test_upload_attachment(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, issue = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    upload = _make_upload_file()
    attachment = upload_attachment(db, issue.id, reporter.id, upload)
    assert attachment.id
    assert attachment.original_name == "screenshot.png"
    assert attachment.content_type == "image/png"
    assert attachment.file_size == len(b"fake-image-data")
    assert os.path.exists(attachment.file_path)

    # cleanup
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)


def test_upload_attachment_issue_not_found(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    user = make_user(email="a@test.com")
    emp = make_employee(user, dept.id)
    with pytest.raises(HTTPException) as exc:
        upload_attachment(db, 999, emp.id, _make_upload_file())
    assert exc.value.status_code == 404


def test_get_issue_attachments(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, issue = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    a1 = upload_attachment(db, issue.id, reporter.id, _make_upload_file("a.png"))
    a2 = upload_attachment(db, issue.id, reporter.id, _make_upload_file("b.png"))

    attachments = get_issue_attachments(db, issue.id)
    assert len(attachments) == 2

    for a in [a1, a2]:
        if os.path.exists(a.file_path):
            os.remove(a.file_path)


def test_delete_attachment(db, make_department, make_user, make_employee, make_project, assign):
    admin, reporter, issue = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    attachment = upload_attachment(db, issue.id, reporter.id, _make_upload_file())
    path = attachment.file_path

    result = delete_attachment(db, attachment.id)
    assert result["message"] == "Attachment deleted successfully."
    assert not os.path.exists(path)
    assert get_issue_attachments(db, issue.id) == []


def test_delete_attachment_not_found(db):
    with pytest.raises(HTTPException) as exc:
        delete_attachment(db, 999)
    assert exc.value.status_code == 404


# --------------------------- Endpoint tests ---------------------------


def test_attachment_endpoints_flow(client, db, make_department, make_user, make_employee, make_project, assign):
    from apps.schemas.issue import IssueCreate
    from apps.services.issue import create_issue
    from apps.services.jwt import create_access_token

    admin, reporter, issue = _setup(
        db, make_department, make_user, make_employee, make_project, assign
    )
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    # upload
    resp = client.post(
        f"/attachments/issue/{issue.id}",
        headers=headers,
        files={"file": ("screenshot.png", b"fake-image-data", "image/png")},
    )
    assert resp.status_code == 200
    attachment = resp.json()
    assert attachment["original_name"] == "screenshot.png"

    # list
    resp = client.get(f"/attachments/issue/{issue.id}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # delete
    resp = client.delete(f"/attachments/{attachment['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Attachment deleted"


def test_attachment_upload_issue_not_found(client, db, make_department, make_user, make_employee):
    from apps.services.jwt import create_access_token

    admin = make_user(role="ADMIN", email="admin@test.com")
    make_employee(admin, make_department(name="CSE").id)
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': admin.email})}"}

    resp = client.post(
        "/attachments/issue/999",
        headers=headers,
        files={"file": ("screenshot.png", b"fake-image-data", "image/png")},
    )
    assert resp.status_code == 404
