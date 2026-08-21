import logging

from app.core.email.email_service_interface import IEmailService

logger = logging.getLogger(__name__)


class ConsoleEmailService(IEmailService):
    """No-op: only logs. Used in tests so the suite never depends on network
    access to a real (or fake) SMTP/HTTP endpoint.
    """

    async def send(self, to: str, subject: str, body: str) -> None:
        logger.info(f"[email] to={to} subject={subject!r}")
