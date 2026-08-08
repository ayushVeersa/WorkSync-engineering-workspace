from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.models.user import User
from apps.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from apps.core.security import get_current_user
from apps.services.employee import (
    get_employee_by_user_id,
)
from apps.services.comment import (
    get_issue_comments,
    create_comment,
    update_comment,
    delete_comment,
)

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


@router.get(
    "/issue/{issue_id}",
    response_model=list[CommentResponse],
)
def comments(
    issue_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_issue_comments(
        db,
        issue_id,
    )


@router.post(
    "/issue/{issue_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    issue_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = get_employee_by_user_id(
        db,
        current_user.id,
    )

    return create_comment(
        db=db,
        issue_id=issue_id,
        payload=payload,
        employee_id=employee.id,
    )


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update(
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = get_employee_by_user_id(
        db,
        current_user.id,
    )

    return update_comment(
        db,
        comment_id,
        payload,
        employee,
    )



@router.delete(
    "/{comment_id}",
)
def delete(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = get_employee_by_user_id(
        db,
        current_user.id,
    )

    return delete_comment(
        db,
        comment_id,
        employee,
    )