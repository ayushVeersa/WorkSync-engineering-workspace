from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.employee import Employee
from apps.models.project import Project
from apps.models.employee_project import EmployeeProject


def assign_employee_to_project(
    db: Session,
    employee_id: int,
    project_id: int,
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    existing = (
        db.query(EmployeeProject)
        .filter(
            EmployeeProject.employee_id == employee_id,
            EmployeeProject.project_id == project_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee already assigned",
        )

    assignment = EmployeeProject(
        employee_id=employee_id,
        project_id=project_id,
    )

    db.add(assignment)
    db.commit()

    return {
        "message": "Employee assigned successfully"
    }



def remove_employee_from_project(
    db: Session,
    employee_id: int,
    project_id: int,
):
    assignment = (
        db.query(EmployeeProject)
        .filter(
            EmployeeProject.employee_id == employee_id,
            EmployeeProject.project_id == project_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    db.delete(assignment)
    db.commit()

    return {
        "message": "Employee removed successfully"
    }


def get_project_members(
    db: Session,
    project_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project.employees


def get_employee_projects(
    db: Session,
    employee_id: int,
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee.projects
