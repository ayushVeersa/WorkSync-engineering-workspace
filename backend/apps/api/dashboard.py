from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.schemas.role import Role
from apps.core.permission import require_roles
from apps.models.user import User
from apps.core.security import get_current_user

from apps.services.employee import (
    get_employee_by_user_id,
)

from apps.services.dashboard import (
    get_dashboard_summary,
    get_my_work,
    issues_by_status,
    issues_by_priority,
    project_overview,
)

from apps.schemas.dashboard import (
    DashboardSummary,
    MyWorkSummary,
    IssueStatusSummary,
    IssuePrioritySummary,
    ProjectOverview,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def summary(
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    return get_dashboard_summary(db)


@router.get(
    "/my-work",
    response_model=MyWorkSummary,
)
def my_work(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_roles(Role.ADMIN, Role.MANAGER))
):

    employee = get_employee_by_user_id(
        db,
        current_user.id,
    )

    return get_my_work(
        db,
        employee.id,
    )


@router.get(
    "/issues/status",
    response_model=list[IssueStatusSummary],
)
def status(
    db: Session = Depends(get_db),
    _ = Depends(require_roles(Role.ADMIN, Role.MANAGER))
):
    return issues_by_status(db)


@router.get(
    "/issues/priority",
    response_model=list[IssuePrioritySummary],
)
def priority(
    db: Session = Depends(get_db),
    _ = Depends(require_roles(Role.ADMIN, Role.MANAGER))
):
    return issues_by_priority(db)


@router.get(
    "/projects",
    response_model=list[ProjectOverview],
)
def projects(
    db: Session = Depends(get_db),
    _ = Depends(require_roles(Role.ADMIN, Role.MANAGER)),
):
    return project_overview(db)

