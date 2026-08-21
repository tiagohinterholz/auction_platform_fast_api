from app.core.email.email_service_interface import IEmailService
from app.modules.users.domain.events.users_events import UserCreatedEvent


class UserCreatedWelcomeEmailHandler:
    """The event payload already carries name/email, so this handler needs
    no repository/DB session.
    """

    def __init__(self, email_service: IEmailService):
        self.email_service = email_service

    async def handle(self, event: UserCreatedEvent) -> None:
        name = event.payload["name"]
        email = event.payload["email"]

        await self.email_service.send(
            to=email,
            subject="Bem-vindo à Auction Platform!",
            body=f"Olá {name}, sua conta foi criada com sucesso. Boas compras (e bons lances)!",
        )
