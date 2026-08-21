from app.core.config import settings
from app.core.email.console_email_service import ConsoleEmailService
from app.core.email.email_service_interface import IEmailService
from app.core.email.mailpit_email_service import MailpitEmailService
from app.core.email.resend_email_service import ResendEmailService


def get_email_service() -> IEmailService:
    if settings.EMAIL_PROVIDER == "resend":
        return ResendEmailService()
    if settings.EMAIL_PROVIDER == "console":
        return ConsoleEmailService()
    return MailpitEmailService()
