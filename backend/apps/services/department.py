from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.department import Department
from apps.schemas.department import DepartmentRequest, DepartmentUpdate
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_all_departments(
    db: Session,
    skip: int = 0,
    limit: int = 10
):

    departments = (
        db.query(Department)
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.info("Fetched all departments, count=%s, skip=%s, limit=%s", len(departments), skip, limit)
    return departments


def get_department(
    db: Session,
    dept_id: int
) -> Department:

    dept = (
        db.query(Department)
        .filter(Department.id == dept_id)
        .first()
    )

    if dept is None:
        logger.warning("Department not found for id=%s", dept_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No department found"
        )

    logger.info("Fetched department id=%s", dept_id)
    return dept


def create_deparment(
    db: Session,
    payload: DepartmentRequest
) -> Department:

    existing = (
        db.query(Department)
        .filter(Department.name == payload.name)
        .first()
    )

    if existing:
        logger.warning("Department already exists with name=%s", payload.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department with this id already exists"
        )

    dept = Department(
        name=payload.name,
        description=payload.description
    )

    db.add(dept)
    db.commit()
    db.refresh(dept)

    logger.info("Created department id=%s name=%s", dept.id, dept.name)
    return dept


def update_department(
    db: Session,
    dept_id: int,
    department_update: DepartmentUpdate
) -> Department:

    dept = get_department(db, dept_id)

    update_dept = department_update.model_dump(exclude_unset=True)

    for key, value in update_dept.items():
        setattr(dept, key, value)

    db.commit()
    db.refresh(dept)

    logger.info("Updated department id=%s with fields=%s", dept_id, list(update_dept.keys()))
    return dept


# will add soft delete later
def delete_department(db: Session, dept_id: int):

    dept = get_department(db, dept_id)

    db.delete(dept)
    db.commit()

    logger.info("Deleted department id=%s", dept_id)
    return {
        "message": "Department deleted successfully"
    }
