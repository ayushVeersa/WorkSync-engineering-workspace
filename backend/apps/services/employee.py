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


def get_employee(db: Session, employee_id: int) -> Employee:

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return employee


def get_employees(db: Session, skip: int = 0, limit: int = 10):

    return (
        db.query(Employee)
        .filter(Employee.is_active.is_(True))
        .offset(skip)
        .limit(limit)
        .all()
    )


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


    department = (
        db.query(Department)
        .filter(Department.id == payload.department_id)
        .first()
    )

    if department is None:
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

    return employee


def delete_employee(db: Session, employee_id: int):

    employee = get_employee(db, employee_id)

    employee.is_active = False

    db.commit()

    return {
        "message": "Employee deleted successfully"
    }
