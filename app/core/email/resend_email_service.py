import asyncio

import resend

from app.core.config import settings
from app.core.email.email_service_interface import IEmailService


class ResendEmailService(IEmailService):
    """Production: real delivery via Resend's HTTP API.

    The official `resend` SDK is synchronous, so the call is offloaded to a
    thread to avoid blocking the event loop.
    """

    def __init__(self) -> None:
        resend.api_key = settings.RESEND_API_KEY

    async def send(self, to: str, subject: str, body: str) -> None:
        await asyncio.to_thread(
            resend.Emails.send,
            {
                "from": settings.EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "text": body,
            },
        )
