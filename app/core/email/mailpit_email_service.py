from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.core.email.email_service_interface import IEmailService


class MailpitEmailService(IEmailService):
    """Dev-only: sends real SMTP traffic to a local Mailpit container, which
    never delivers anywhere — it just holds the message for inspection at
    Mailpit's own web UI.
    """

    async def send(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=settings.MAILPIT_SMTP_HOST,
            port=settings.MAILPIT_SMTP_PORT,
        )
