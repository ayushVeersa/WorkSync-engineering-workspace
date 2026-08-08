from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)

from sqlalchemy.orm import Session

from apps.db.database import get_db
from apps.core.security import get_current_user
from apps.services.employee import get_employee_by_user_id
from apps.services.attachment import (
    upload_attachment,
    get_issue_attachments,
    delete_attachment,
)

router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)


@router.post(
    "/issue/{issue_id}",
)
def upload(
    issue_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = get_employee_by_user_id(
        db,
        current_user.id,
    )

    return upload_attachment(
        db,
        issue_id,
        employee.id,
        file,
    )


@router.get(
    "/issue/{issue_id}",
)
def list_attachments(
    issue_id: int,
    db: Session = Depends(get_db),
):
    return get_issue_attachments(
        db,
        issue_id,
    )


@router.delete(
    "/{attachment_id}",
)
def delete(
    attachment_id: int,
    db: Session = Depends(get_db),
):
    delete_attachment(
        db,
        attachment_id,
    )

    return {
        "message": "Attachment deleted"
    }