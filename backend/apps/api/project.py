from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.core.permission import require_roles
from backend.apps.schemas.role import Role

from apps.models.user import User
from apps.core.security import get_current_user

from apps.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)

from apps.services.project import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_all_projects(
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
            Role.EMPLOYEE,
        )
    ),
):
    return get_projects(db)


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
