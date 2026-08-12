import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apps.core.config import settings


# Non-blocking worker function for sending email via SMTP
def send_smtp_email(recipient: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = settings.smtp_from
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()  
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_from, recipient, msg.as_string())
    except Exception as e:
        # In a real environment, log this exception locally 
        print(f"SMTP Error: {str(e)}")


# @router.post("/send-email", status_code=status.HTTP_202_ACCEPTED)
# async def trigger_email(payload: EmailRequest, background_tasks: BackgroundTasks):
#     """
#     Triggers an email dispatch task and instantly unlocks the client connection 
#     by throwing the SMTP transmission work to a background thread handler.
#     """
#     background_tasks.add_task(
#         send_smtp_email, 
#         recipient=payload.recipient, 
#         subject=payload.subject, 
#         body=payload.body
#     )
#     return {"message": "Email dispatch successfully added to background queue"}
