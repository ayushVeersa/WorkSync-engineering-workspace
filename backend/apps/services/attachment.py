from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import os
import uuid

from apps.models.issue import Issue
from apps.models.attachment import Attachment
from apps.core.logging import get_logger

logger = get_logger(__name__)

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
        logger.warning("Issue not found for id=%s while uploading attachment", issue_id)
        raise HTTPException(
            404,
            "Issue not found",
        )

    extension = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4()}{extension}"

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

    logger.info("Uploaded attachment id=%s name=%s size=%s bytes for issue_id=%s",
                attachment.id, attachment.original_name, len(contents), issue_id)
    return attachment


def get_issue_attachments(
    db: Session,
    issue_id: int,
):
    attachments = (
        db.query(Attachment)
        .filter(
            Attachment.issue_id == issue_id
        )
        .all()
    )
    logger.info("Fetched attachments for issue_id=%s, count=%s", issue_id, len(attachments))
    return attachments


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
        logger.warning("Attachment not found for id=%s", attachment_id)
        raise HTTPException(
            404,
            "Attachment not found",
        )

    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)
        logger.info("Removed attachment file from disk: %s", attachment.file_path)

    db.delete(attachment)
    db.commit()

    logger.info("Deleted attachment id=%s", attachment_id)
    return {
        "message": "Attachment deleted successfully."
    }
