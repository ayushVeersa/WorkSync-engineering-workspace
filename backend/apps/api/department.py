from fastapi import HTTPException, status, Depends, APIRouter, Query
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.core.permission import require_roles
from backend.apps.schemas.role import Role
from apps.services.department import (
    get_department,
    get_all_departments,
    create_deparment,
    delete_department,
    update_department
)
from apps.schemas.department import (
    DepartmentRequest,
    DepartmentResponse,
    DepartmentUpdate
)


router = APIRouter(
    prefix="/department",
    tags=["Department"]
)


@router.get(
    "",
    response_model=list[DepartmentResponse]
)
def get_departments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _ = Depends(require_roles(Role.ADMIN))
):
    return get_all_departments(db, skip, limit)


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department_by_id(
    dept_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(Role.ADMIN))
):
    return get_department(db, dept_id)


# @router.get("/me", response_model=DepartmentResponse)
# def get_my_department():


@router.post("", response_model=DepartmentResponse)
def create_new_department(
    department: DepartmentRequest,
    dependencies = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    return create_deparment(db, department)


@router.put("", response_model=DepartmentResponse)
def update_existing_department(
    dept_id: int,
    department: DepartmentUpdate,
    _ = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    return update_department(db, dept_id, department)


@router.delete("")
def delete_existing_department(
    dept_id: int,
    dependencies = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    return delete_department(db, dept_id)
