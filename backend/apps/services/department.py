from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.department import Department
from apps.schemas.department import DepartmentRequest, DepartmentUpdate



def get_all_departments(
    db: Session,
    skip: int = 0,
    limit: int = 10
):

    return (
        db.query(Department)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_department(
    db: Session,
    dept_id: int
) -> Department:

    # if dept_id is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Dept. id cannot be empty"
    #     )

    dept = (
        db.query(Department)
        .filter(Department.id==dept_id)
        .first()
    )

    if dept is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No department found"
        )

    return dept


def create_deparment(
    db: Session,
    payload: DepartmentRequest
) -> Department:

    existing = (
        db.query(Department)
        .filter(Department.name==payload.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department with this id already exists"
        )

    dept = Department(
        #id = payload.id,
        name = payload.name,
        description = payload.description
    )

    db.add(dept)
    db.commit()
    db.refresh(dept)

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

    return dept


# will add soft delete later
def delete_department(db: Session, dept_id: int):

    dept = get_department(db, dept_id)

    db.delete(dept)
    db.commit()

    return {
        "message": "Department deleted successfully"
    }
