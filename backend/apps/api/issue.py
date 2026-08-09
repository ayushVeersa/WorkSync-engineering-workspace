from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
)

from apps.db.database import get_db
from apps.models.user import User
from apps.models.employee import Employee
from apps.core.security import get_current_user
from apps.core.permission import require_roles
from apps.schemas.role import Role
from apps.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueStatus,
    IssuePriority,
    IssueType,
)
from apps.schemas.employee import EmployeeResponse
from apps.services.employee import get_employee_by_user_id
from apps.services.issue import (
    get_issue,
    get_all_issues,
    create_issue,
    update_issue,
    delete_issue,
    get_project_issues,
    get_my_issues,
    get_issues_by_status,
    get_issues_by_priority,
)


router = APIRouter(
    prefix="/issues",
    tags=["Issues"],
)


@router.get(
    "",
    response_model=list[IssueResponse],
)
def get_all(
    status: IssueStatus | None = Query(default=None),
    priority: IssuePriority | None = Query(default=None),
    issue_type: IssueType | None = Query(default=None),
    assignee_id: int | None = Query(default=None),
    project_id: int | None = Query(default=None),
    search: str | None = Query(default=None, description="Search by title or description"),
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
    return get_all_issues(
        db=db,
        status=status,
        priority=priority,
        issue_type=issue_type,
        assignee_id=assignee_id,
        project_id=project_id,
        search=search,
        skip=skip,
        limit=limit,
    )



@router.get(
    "/me",
    response_model=list[IssueResponse],
)
def my_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = get_employee_by_user_id(
        db,
        current_user.id,
    )

    return get_my_issues(
        db,
        employee.id,
    )


@router.get(
    "/project/{project_id}",
    response_model=list[IssueResponse],
)
def project_issues(
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
    return get_project_issues(
        db,
        project_id,
    )


# @router.get(
#     "/status/{issue_status}",
#     response_model=list[IssueResponse],
# )
# def issues_by_status(
#     issue_status: IssueStatus,
#     db: Session = Depends(get_db),
#     _: User = Depends(
#         require_roles(
#             Role.ADMIN,
#             Role.MANAGER,
#             Role.EMPLOYEE,
#         )
#     ),
# ):
#     return get_issues_by_status(
#         db,
#         issue_status,
#     )


# @router.get(
#     "/priority/{priority}",
#     response_model=list[IssueResponse],
# )
# def issues_by_priority(
#     priority: IssuePriority,
#     db: Session = Depends(get_db),
#     _: User = Depends(
#         require_roles(
#             Role.ADMIN,
#             Role.MANAGER,
#             Role.EMPLOYEE,
#         )
#     ),
# ):
#     return get_issues_by_priority(
#         db,
#         priority,
#     )


@router.get(
    "/{issue_id}",
    response_model=IssueResponse,
)
def get_by_id(
    issue_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
            Role.EMPLOYEE,
        )
    ),
):
    return get_issue(db, issue_id)


@router.post(
    "",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = get_employee_by_user_id(
        db,
        current_user.id,
    )

    return create_issue(
        db=db,
        issue=payload,
        reporter_id=employee.id,
    )


@router.put(
    "/{issue_id}",
    response_model=IssueResponse,
)
def update(
    issue_id: int,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
            Role.EMPLOYEE,
        )
    ),
):
    return update_issue(
        db,
        issue_id,
        payload,
    )


@router.delete(
    "/{issue_id}",
)
def delete(
    issue_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            Role.ADMIN,
            Role.MANAGER,
        )
    ),
):
    return delete_issue(
        db,
        issue_id,
    )
