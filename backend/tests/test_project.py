"""
Tests for project service functions and endpoints.
"""

import pytest
from fastapi import HTTPException

from apps.schemas.role import Role
from apps.schemas.project import ProjectStatus
from apps.services.project import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project,
)
from apps.schemas.project import ProjectCreate, ProjectUpdate


def project_payload(**kw):
    payload = {
        "name": "Engineering Workspace",
        "description": "Internal suite",
        "status": "ACTIVE",
    }
    payload.update(kw)
    return payload


# --------------------------- Service tests ---------------------------


def test_get_projects_empty(db):
    assert get_projects(db) == []


def test_get_project_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_project(db, 999)
    assert exc.value.status_code == 404


def test_create_project(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    user = make_user(email="owner@test.com")
    emp = make_employee(user, dept.id)

    project = create_project(
        db,
        ProjectCreate(**project_payload()),
        owner_id=emp.id,
    )
    assert project.id
    assert project.name == "Engineering Workspace"
    assert project.owner_id == emp.id


def test_get_project(db, make_project):
    project = make_project("Project A", 1)
    fetched = get_project(db, project.id)
    assert fetched.id == project.id
    assert fetched.name == "Project A"


def test_update_project(db, make_project):
    project = make_project("Project A", 1)
    updated = update_project(
        db,
        project.id,
        ProjectUpdate(status=ProjectStatus.ON_HOLD),
    )
    assert updated.status == ProjectStatus.ON_HOLD


def test_delete_project(db, make_project):
    project = make_project("Project A", 1)
    result = delete_project(db, project.id)
    assert result["message"] == "Project deleted successfully"
    assert get_projects(db) == []


# --------------------------- Endpoint tests ---------------------------


def _make_employee_for_user(db, user, dept):
    from apps.models.employee import Employee

    emp = Employee(
        user_id=user.id,
        department_id=dept.id,
        designation="Manager",
        age=30,
        is_active=True,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def test_project_endpoints_flow(client, db, make_department, make_user_with_token):
    admin, headers = make_user_with_token(role=Role.ADMIN)
    dept = make_department(name="CSE")
    emp = _make_employee_for_user(db, admin, dept)

    # create
    resp = client.post("/projects", headers=headers, json=project_payload())
    assert resp.status_code == 201
    proj = resp.json()
    assert proj["name"] == "Engineering Workspace"
    assert proj["owner_id"] == emp.id

    # list
    resp = client.get("/projects", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # get by id
    resp = client.get(f"/projects/{proj['id']}", headers=headers)
    assert resp.status_code == 200

    # update
    resp = client.put(
        f"/projects/{proj['id']}",
        headers=headers,
        json={"status": "ON_HOLD"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ON_HOLD"

    # delete
    resp = client.delete(f"/projects/{proj['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Project deleted successfully"


def test_project_delete_requires_admin(client, db, make_department, make_user_with_token):
    manager, headers = make_user_with_token(role=Role.MANAGER)
    dept = make_department(name="CSE")
    emp = _make_employee_for_user(db, manager, dept)

    resp = client.post("/projects", headers=headers, json=project_payload())
    assert resp.status_code == 201
    proj = resp.json()

    # manager cannot delete (admin only)
    resp = client.delete(f"/projects/{proj['id']}", headers=headers)
    assert resp.status_code == 403


def test_project_not_found(client, db, make_user_with_token):
    _, headers = make_user_with_token(role=Role.ADMIN)
    resp = client.get("/projects/999", headers=headers)
    assert resp.status_code == 404
