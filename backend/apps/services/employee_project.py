from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.employee import Employee
from apps.models.project import Project
from apps.models.employee_project import EmployeeProject
from apps.core.logging import get_logger

logger = get_logger(__name__)


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
        logger.warning("Employee not found for id=%s while assigning to project", employee_id)
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
        logger.warning("Project not found for id=%s while assigning employee", project_id)
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
        logger.warning("Employee %s already assigned to project %s", employee_id, project_id)
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

    logger.info("Assigned employee id=%s to project id=%s", employee_id, project_id)
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
        logger.warning("Assignment not found for employee %s and project %s", employee_id, project_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    db.delete(assignment)
    db.commit()

    logger.info("Removed employee id=%s from project id=%s", employee_id, project_id)
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
        logger.warning("Project not found for id=%s while fetching members", project_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    logger.info("Fetched members for project id=%s, count=%s", project_id, len(project.employees))
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
        logger.warning("Employee not found for id=%s while fetching projects", employee_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    logger.info("Fetched projects for employee id=%s, count=%s", employee_id, len(employee.projects))
    return employee.projects
