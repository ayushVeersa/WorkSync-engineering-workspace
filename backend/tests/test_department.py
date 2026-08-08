"""
Tests for department service functions and endpoints.
"""

import pytest
from fastapi import HTTPException

from apps.schemas.role import Role
from apps.services.department import (
    get_all_departments,
    get_department,
    create_deparment,
    update_department,
    delete_department,
)
from apps.schemas.department import DepartmentRequest, DepartmentUpdate


def dept_payload(name="CSE", description="Computer Science"):
    return {"name": name, "description": description}


# --------------------------- Service tests ---------------------------


def test_get_all_departments_empty(db):
    assert get_all_departments(db) == []


def test_get_department_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_department(db, 999)
    assert exc.value.status_code == 400
    assert exc.value.detail == "No department found"


def test_create_department(db):
    dept = create_deparment(db, DepartmentRequest(**dept_payload()))
    assert dept.id
    assert dept.name == "CSE"
    assert dept.description == "Computer Science"


def test_create_department_duplicate(db):
    create_deparment(db, DepartmentRequest(**dept_payload()))
    with pytest.raises(HTTPException) as exc:
        create_deparment(db, DepartmentRequest(**dept_payload()))
    assert exc.value.status_code == 409


def test_get_department(db, make_department):
    dept = make_department(name="ECE")
    fetched = get_department(db, dept.id)
    assert fetched.id == dept.id
    assert fetched.name == "ECE"


def test_update_department(db, make_department):
    dept = make_department(name="ECE")
    updated = update_department(
        db,
        dept.id,
        DepartmentUpdate(description="Electronics"),
    )
    assert updated.description == "Electronics"
    assert updated.name == "ECE"


def test_delete_department(db, make_department):
    dept = make_department(name="ECE")
    result = delete_department(db, dept.id)
    assert result["message"] == "Department deleted successfully"
    assert get_all_departments(db) == []


# --------------------------- Endpoint tests ---------------------------


def test_department_endpoints_flow(client, db, make_user_with_token):
    _, headers = make_user_with_token(role=Role.ADMIN)

    # create
    resp = client.post("/department", headers=headers, json=dept_payload())
    assert resp.status_code == 200
    dept = resp.json()
    assert dept["name"] == "CSE"

    # list
    resp = client.get("/department", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # get by id
    resp = client.get(f"/department/{dept['id']}", headers=headers)
    assert resp.status_code == 200

    # update
    resp = client.put(
        "/department",
        headers=headers,
        params={"dept_id": dept["id"]},
        json={"description": "Updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated"

    # delete
    resp = client.delete(
        "/department",
        headers=headers,
        params={"dept_id": dept["id"]},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Department deleted successfully"


def test_department_requires_admin(client, db, make_user_with_token):
    _, headers = make_user_with_token(role=Role.EMPLOYEE)
    resp = client.post("/department", headers=headers, json=dept_payload())
    assert resp.status_code == 403


def test_department_get_not_found(client, db, make_user_with_token):
    _, headers = make_user_with_token(role=Role.ADMIN)
    resp = client.get("/department/999", headers=headers)
    assert resp.status_code == 400
