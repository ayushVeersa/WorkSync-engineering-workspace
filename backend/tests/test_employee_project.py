"""
Tests for employee-project assignment service functions and endpoints.
"""

import pytest
from fastapi import HTTPException

from apps.schemas.role import Role
from apps.services.employee_project import (
    assign_employee_to_project,
    remove_employee_from_project,
    get_project_members,
    get_employee_projects,
)


# --------------------------- Service tests ---------------------------


def test_assign_employee_to_project(db, make_department, make_user, make_employee, make_project):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)

    result = assign_employee_to_project(db, emp2.id, project.id)
    assert result["message"] == "Employee assigned successfully"


def test_assign_employee_not_found(db, make_project):
    project = make_project("Project A", 1)
    with pytest.raises(HTTPException) as exc:
        assign_employee_to_project(db, 999, project.id)
    assert exc.value.status_code == 404


def test_assign_project_not_found(db, make_department, make_user, make_employee):
    dept = make_department(name="CSE")
    user = make_user(email="a@test.com")
    emp = make_employee(user, dept.id)
    with pytest.raises(HTTPException) as exc:
        assign_employee_to_project(db, emp.id, 999)
    assert exc.value.status_code == 404


def test_assign_duplicate(db, make_department, make_user, make_employee, make_project, assign):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)

    with pytest.raises(HTTPException) as exc:
        assign_employee_to_project(db, emp2.id, project.id)
    assert exc.value.status_code == 409


def test_get_project_members(db, make_department, make_user, make_employee, make_project, assign):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp1.id, project.id)
    assign(emp2.id, project.id)

    members = get_project_members(db, project.id)
    assert len(members) == 2


def test_get_project_members_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_project_members(db, 999)
    assert exc.value.status_code == 404


def test_get_employee_projects(db, make_department, make_user, make_employee, make_project, assign):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    p1 = make_project("Project A", emp1.id)
    p2 = make_project("Project B", emp1.id)
    assign(emp2.id, p1.id)
    assign(emp2.id, p2.id)

    projects = get_employee_projects(db, emp2.id)
    assert len(projects) == 2


def test_get_employee_projects_not_found(db):
    with pytest.raises(HTTPException) as exc:
        get_employee_projects(db, 999)
    assert exc.value.status_code == 404


def test_remove_employee_from_project(db, make_department, make_user, make_employee, make_project, assign):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)
    assign(emp2.id, project.id)

    result = remove_employee_from_project(db, emp2.id, project.id)
    assert result["message"] == "Employee removed successfully"
    assert get_project_members(db, project.id) == []


def test_remove_employee_not_assigned(db, make_department, make_user, make_employee, make_project):
    dept = make_department(name="CSE")
    u1 = make_user(email="a@test.com")
    u2 = make_user(email="b@test.com")
    emp1 = make_employee(u1, dept.id)
    emp2 = make_employee(u2, dept.id)
    project = make_project("Project A", emp1.id)

    with pytest.raises(HTTPException) as exc:
        remove_employee_from_project(db, emp2.id, project.id)
    assert exc.value.status_code == 404


# --------------------------- Endpoint tests ---------------------------


def _setup(client, db, make_department, make_user_with_token, make_project, make_employee):
    admin, headers = make_user_with_token(role=Role.ADMIN)
    dept = make_department(name="CSE")
    emp = make_employee(admin, dept.id)
    project = make_project("Project A", emp.id)
    return headers, emp, project


def test_assign_endpoint_flow(client, db, make_department, make_user_with_token, make_project, make_employee, make_user):
    admin, headers = make_user_with_token(role=Role.ADMIN)
    dept = make_department(name="CSE")
    emp = make_employee(admin, dept.id)
    project = make_project("Project A", emp.id)

    # create another employee to assign
    other_user = make_user(email="other@test.com")
    other_emp = make_employee(other_user, dept.id)

    # assign
    resp = client.post(
        f"/projects/{project.id}/members/{other_emp.id}",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Employee assigned successfully"

    # list members
    resp = client.get(f"/projects/{project.id}/members", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # employee projects
    resp = client.get(f"/projects/employees/{other_emp.id}/projects", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # remove
    resp = client.delete(
        f"/projects/{project.id}/members/{other_emp.id}",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Employee removed successfully"


def test_assign_member_requires_admin_or_manager(client, db, make_department, make_user_with_token, make_project, make_employee, make_user):
    employee_user, headers = make_user_with_token(role=Role.EMPLOYEE)
    dept = make_department(name="CSE")
    emp = make_employee(employee_user, dept.id)
    project = make_project("Project A", emp.id)

    resp = client.post(
        f"/projects/{project.id}/members/{emp.id}",
        headers=headers,
    )
    assert resp.status_code == 403
