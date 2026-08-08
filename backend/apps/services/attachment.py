from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import os
import uuid

from apps.models.issue import Issue
from apps.models.attachment import Attachment

UPLOAD_DIR = "uploads/issues"

if not os.path.isdir(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_attachment(
    db: Session,
    issue_id: int,
    employee_id: int,
    file: UploadFile,
):
    """
    Upload attachments using UploadFile(from fastapi)
    """
    issue = (
        db.query(Issue)
        .filter(Issue.id == issue_id)
        .first()
    )

    if not issue:
        raise HTTPException(
            404,
            "Issue not found",
        )

    extension = os.path.splitext(file.filename)[1]
    print(extension)
    stored_name = f"{uuid.uuid4()}{extension}"
    print(stored_name)

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_name,
    )

    contents = file.file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    attachment = Attachment(
        original_name=file.filename,
        stored_name=stored_name,
        file_path=file_path,
        content_type=file.content_type,
        file_size=len(contents),
        issue_id=issue_id,
        uploaded_by=employee_id,
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment



def get_issue_attachments(
    db: Session,
    issue_id: int,
):
    return (
        db.query(Attachment)
        .filter(
            Attachment.issue_id == issue_id
        )
        .all()
    )


def delete_attachment(
    db: Session,
    attachment_id: int,
):

    attachment = (
        db.query(Attachment)
        .filter(
            Attachment.id == attachment_id
        )
        .first()
    )

    if not attachment:
        raise HTTPException(
            404,
            "Attachment not found",
        )

    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    db.delete(attachment)
    db.commit()

    return {
        "message": "Attachment deleted successfully."
    }