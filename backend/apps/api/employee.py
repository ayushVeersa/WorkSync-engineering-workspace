from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.core.security import get_current_user
from apps.core.permission import require_roles
from apps.schemas.role import Role
from apps.models.user import User
from apps.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeRegistrationRequest,
)
from apps.services.employee import (
    get_employee,
    get_employees,
    create_employee,
    update_employee,
    delete_employee,
    get_employee_by_user_id,
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)

@router.get(
    "",
    response_model=list[EmployeeResponse],
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
)
def get_all_employees(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None, description="Search by name or designation"),
    department_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _ = Depends(get_current_user),
):
    """
    Get all Employee if you are an ADMIN or MANAGER
    """
    #Later: Manager can get employees of their own dept. only
    return get_employees(db, skip, limit, search=search, department_id=department_id)


@router.get("/me", response_model=EmployeeResponse)
def get_current_employee(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return get_employee_by_user_id(db, user.id)


@router.get("/{employee_id}",response_model=EmployeeResponse)
def get_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
    _ = Depends(get_current_user),
):
    """
    Fetch employee by employee ID.
    """
    return get_employee(db, employee_id)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
def create_new_employee(
    payload: EmployeeRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new Employee, only if you are an ADMIN
    """
    return create_employee(db, payload)


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.MANAGER))],
)
def update_existing_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update Existing Employee(not User, just Employee)
    """
    return update_employee(
        db,
        employee_id,
        employee,
    )


@router.delete(
    "/{employee_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
)
def delete_existing_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete the employee using Employee ID
    """
    return delete_employee(
        db,
        employee_id,
    )


