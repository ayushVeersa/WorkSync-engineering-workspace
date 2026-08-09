from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.core.permission import require_roles
from apps.schemas.role import Role

from apps.models.user import User
from apps.core.security import get_current_user

from apps.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectStatus,
)
from apps.schemas.board import BoardResponse

from apps.services.project import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project,
)
from apps.services.board import get_project_board

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_all_projects(
    search: str | None = Query(default=None, description="Search by project name"),
    status: ProjectStatus | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
            Role.EMPLOYEE,
        )
    ),
):
    return get_projects(
        db,
        search=search,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{project_id}/board",
    response_model=BoardResponse,
)
def get_board(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
            Role.EMPLOYEE,
        )
    ),
):
    return get_project_board(
        db,
        project_id,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
            Role.EMPLOYEE,
        )
    ),
):
    return get_project(db, project_id)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
        )
    ),
):
    return create_project(
        db=db,
        project=project,
        owner_id=current_user.employee.id,
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
        )
    ),
):
    return update_project(
        db,
        project_id,
        project,
    )


@router.delete(
    "/{project_id}",
)
def delete_existing_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
        )
    ),
):
    return delete_project(
        db,
        project_id,
    )
