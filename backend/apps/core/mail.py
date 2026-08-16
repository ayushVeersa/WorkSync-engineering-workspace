import smtplib
from email.message import EmailMessage
from threading import Thread

from apps.core.config import settings
from apps.core.logging import get_logger

logger = get_logger(__name__)


def _build_message(recipient: str, subject: str, body: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    return message


def send_smtp_email(recipient: str, subject: str, body: str):
    message = _build_message(recipient, subject, body)

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port) as server:
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)

        logger.info("Sent SMTP email to %s with subject=%s", recipient, subject)
    except Exception:
        logger.exception("SMTP error while sending email to %s", recipient)


def queue_smtp_email(recipient: str, subject: str, body: str):
    Thread(
        target=send_smtp_email,
        args=(recipient, subject, body),
        daemon=True,
    ).start()


def queue_employee_welcome_email(
    recipient: str,
    name: str,
    designation: str,
    department: str,
):
    subject = "Welcome to WorkSync"
    body = (
        f"Hi {name},\n\n"
        "Welcome to WorkSync. Your employee profile is now active.\n\n"
        f"Designation: {designation}\n"
        f"Department: {department}\n\n"
        "You can sign in to review your work, projects, and tasks.\n"
    )
    queue_smtp_email(recipient, subject, body)


def queue_task_assigned_email(
    recipient: str,
    name: str,
    task_title: str,
    project_name: str,
):
    subject = f"New task assigned: {task_title}"
    body = (
        f"Hi {name},\n\n"
        f"A new task has been assigned to you in the project {project_name}.\n\n"
        f"Task: {task_title}\n\n"
        "Please open WorkSync to review the details.\n"
    )
    queue_smtp_email(recipient, subject, body)


def queue_project_membership_email(
    recipient: str,
    name: str,
    project_name: str,
):
    subject = f"Added to project: {project_name}"
    body = (
        f"Hi {name},\n\n"
        f"You have been added to the project {project_name}.\n\n"
        "You can now view the project board and related tasks in WorkSync.\n"
    )
    queue_smtp_email(recipient, subject, body)
