from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.employee import Employee
from apps.models.user import User
from apps.models.department import Department
from apps.schemas.employee import (
    EmployeeUpdate,
    EmployeeRegistrationRequest,
)
from apps.schemas.user import UserRegister
from apps.services.user_service import create_user
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_employee(db: Session, employee_id: int) -> Employee:

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        logger.warning("Employee not found for id=%s", employee_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    logger.info("Fetched employee id=%s", employee_id)
    return employee


def get_employee_by_user_id(
    db: Session,
    user_id: int
) -> Employee:
    employee = (
        db.query(Employee)
        .filter(Employee.user_id == user_id)
        .first()
    )

    if employee is None:
        logger.warning("Employee not found for user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    logger.info("Fetched employee id=%s for user_id=%s", employee.id, user_id)
    return employee


def get_employees(db: Session, skip: int = 0, limit: int = 10):

    employees = (
        db.query(Employee)
        .filter(Employee.is_active.is_(True))
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.info("Fetched employees list, count=%s, skip=%s, limit=%s", len(employees), skip, limit)
    return employees


def create_employee(
    db: Session,
    payload: EmployeeRegistrationRequest,
) -> Employee:

    # Find/create the backing User
    existing_user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing_user is None:
        user = create_user(
            UserRegister(
                name=payload.name,
                email=payload.email,
                password=payload.password,
                age=payload.age,
                role=payload.role,
            ),
            db,
        )
    else:
        user = existing_user

    logger.info("Resolved backing user id=%s for employee registration email=%s", user.id, payload.email)

    department = (
        db.query(Department)
        .filter(Department.id == payload.department_id)
        .first()
    )

    if department is None:
        logger.warning("Department not found for id=%s while creating employee", payload.department_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
    )

    existing_employee = (
        db.query(Employee)
        .filter(Employee.user_id == user.id)
        .first()
    )

    if existing_employee:
        logger.warning("Employee already exists for user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee already exists",
        )

    employee = Employee(
        user_id=user.id,
        age=payload.age or 0,
        designation=payload.designation,
        department_id=payload.department_id
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    logger.info("Created employee id=%s for user_id=%s", employee.id, user.id)
    return employee


def update_employee(
    db: Session,
    employee_id: int,
    employee_update: EmployeeUpdate,
) -> Employee:

    employee = get_employee(db, employee_id)

    update_data = employee_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    logger.info("Updated employee id=%s with fields=%s", employee_id, list(update_data.keys()))
    return employee


def delete_employee(db: Session, employee_id: int):

    employee = get_employee(db, employee_id)

    employee.is_active = False

    db.commit()

    logger.info("Soft-deleted employee id=%s", employee_id)
    return {
        "message": "Employee deleted successfully"
    }
