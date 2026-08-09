"""
Tests for employee service functions and endpoints.
"""

import pytest
from fastapi import HTTPException

from apps.schemas.role import Role
from apps.services.employee import (
    get_employee,
    get_employee_by_user_id,
    get_employees,
    create_employee,
    update_employee,
    delete_employee,
)
from apps.schemas.employee import (
    EmployeeRegistrationRequest,
    EmployeeUpdate,
)


def employee_payload(**kw):
    payload = {
        "name": "New Employee",
        "email": "newemp@test.com",
        "password": "secret123",
        "designation": "SDE Intern",
        "department_id": 1,
        "role": "EMPLOYEE",
        "age": 25,
    }
    payload.update(kw)
    return payload


# --------------------------- Service tests ---------------------------


def test_get_employee_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_employee(db, 999)
    assert exc.value.status_code == 404


def test_get_employee_by_user_id_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_employee_by_user_id(db, 999)
    assert exc.value.status_code == 404


def test_create_employee(db, make_department):
    dept = make_department(name="CSE")
    employee = create_employee(
        db,
        EmployeeRegistrationRequest(**employee_payload(department_id=dept.id)),
    )
    assert employee.id
    assert employee.designation == "SDE Intern"
    assert employee.user.email == "newemp@test.com"


def test_create_employee_department_not_found(db):
    with pytest.raises(HTTPException) as exc:
        create_employee(
            db,
            EmployeeRegistrationRequest(**employee_payload(department_id=999)),
        )
    assert exc.value.status_code == 404


def test_create_employee_duplicate(db, make_department):
    dept = make_department(name="CSE")
    payload = EmployeeRegistrationRequest(**employee_payload(department_id=dept.id))
    create_employee(db, payload)

    with pytest.raises(HTTPException) as exc:
        create_employee(db, payload)
    assert exc.value.status_code == 409


def test_get_employees(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    make_employee(u1, dept.id)
    make_employee(u2, dept.id)

    employees = get_employees(db)
    assert len(employees) == 2


def test_get_employees_search_and_filters(db, make_department, make_user, make_employee):
    dept1 = make_department(name="CSE")
    dept2 = make_department(name="EEE")
    u1 = make_user(name="Alice", email="alice@test.com")
    u2 = make_user(name="Bob", email="bob@test.com")
    u3 = make_user(name="Carol", email="carol@test.com")
    make_employee(u1, dept1.id, designation="Engineer")
    make_employee(u2, dept1.id, designation="Manager")
    make_employee(u3, dept2.id, designation="Engineer")

    # search by user name
    assert len(get_employees(db, search="ali")) == 1
    assert get_employees(db, search="ali")[0].user.name == "Alice"

    # search by designation
    assert len(get_employees(db, search="engineer")) == 2
    assert len(get_employees(db, search="manager")) == 1

    # filter by department
    assert len(get_employees(db, department_id=dept1.id)) == 2
    assert len(get_employees(db, department_id=dept2.id)) == 1

    # combined search + department
    assert len(get_employees(db, search="engineer", department_id=dept1.id)) == 1
    assert len(get_employees(db, search="engineer", department_id=dept2.id)) == 1

    # pagination
    assert len(get_employees(db, skip=0, limit=2)) == 2
    assert len(get_employees(db, skip=2, limit=2)) == 1


def test_update_employee(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    user = make_user(email="a@test.com")
    emp = make_employee(user, dept.id)

    updated = update_employee(
        db,
        emp.id,
        EmployeeUpdate(designation="Senior Engineer"),
    )
    assert updated.designation == "Senior Engineer"


def test_delete_employee(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    user = make_user(email="a@test.com")
    emp = make_employee(user, dept.id)

    result = delete_employee(db, emp.id)
    assert result["message"] == "Employee deleted successfully"


# --------------------------- Endpoint tests ---------------------------


def test_employee_endpoints_flow(client, db, make_department, make_user_with_token):
    admin, headers = make_user_with_token(role=Role.ADMIN)
    dept = make_department(name="CSE")

    # create
    resp = client.post(
        "/employees",
        headers=headers,
        json=employee_payload(department_id=dept.id),
    )
    assert resp.status_code == 201
    emp = resp.json()
    assert emp["designation"] == "SDE Intern"

    # list
    resp = client.get("/employees", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # get by id
    resp = client.get(f"/employees/{emp['id']}", headers=headers)
    assert resp.status_code == 200

    # make the admin an employee so /employees/me works
    admin_employee = create_employee(
        db,
        EmployeeRegistrationRequest(**employee_payload(
            name=admin.name,
            email=admin.email,
            department_id=dept.id,
            role="ADMIN",
        )),
    )
    assert admin_employee.id

    # get me (admin now has an employee record)
    resp = client.get("/employees/me", headers=headers)
    assert resp.status_code == 200

    # update
    resp = client.put(
        f"/employees/{emp['id']}",
        headers=headers,
        json={"designation": "Senior Dev"},
    )
    assert resp.status_code == 200
    assert resp.json()["designation"] == "Senior Dev"

    # delete
    resp = client.delete(f"/employees/{emp['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Employee deleted successfully"


def test_employee_requires_admin(client, db, make_user_with_token):
    _, headers = make_user_with_token(role=Role.MANAGER)
    resp = client.post("/employees", headers=headers, json=employee_payload())
    assert resp.status_code == 403


def test_employee_not_found(client, db, make_user_with_token):
    _, headers = make_user_with_token(role=Role.ADMIN)
    resp = client.get("/employees/999", headers=headers)
    assert resp.status_code == 404
