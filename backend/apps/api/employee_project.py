from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.services.employee_project import (
    assign_employee_to_project,
    remove_employee_from_project,
    get_project_members,
    get_employee_projects,
)
from apps.schemas.employee_project import AssignmentResponse
from apps.schemas.employee import EmployeeResponse
from apps.schemas.project import ProjectResponse

from apps.core.permission import require_roles
from apps.schemas.role import Role


router = APIRouter(
    prefix="/projects",
    tags=["Project Member Assignment"],
)


@router.get(
    "/{project_id}/members",
    response_model=list[EmployeeResponse],
)
def members(
    project_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.EMPLOYEE)),
):
    return get_project_members(
        db,
        project_id,
    )


@router.post(
    "/{project_id}/members/{employee_id}",
    response_model=AssignmentResponse,
)
def assign_member(
    project_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.ADMIN, Role.MANAGER)),
):
    return assign_employee_to_project(
        db,
        employee_id,
        project_id,
    )


@router.get(
    "/employees/{employee_id}/projects",
    response_model=list[ProjectResponse],
)
def projects(
    employee_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.EMPLOYEE)),
):
    return get_employee_projects(
        db,
        employee_id,
    )


@router.delete(
    "/{project_id}/members/{employee_id}",
    response_model=AssignmentResponse,
)
def remove_member(
    project_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.ADMIN, Role.MANAGER)),
):
    return remove_employee_from_project(
        db,
        employee_id,
        project_id,
    )



