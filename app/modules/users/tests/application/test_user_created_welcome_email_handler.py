import uuid
from unittest.mock import AsyncMock

from app.core.email.email_service_interface import IEmailService
from app.modules.users.application.handlers.user_created_welcome_email_handler import (
    UserCreatedWelcomeEmailHandler,
)
from app.modules.users.domain.events.users_events import UserCreatedEvent


class TestUserCreatedWelcomeEmailHandler:

    async def test_sends_welcome_email_with_name_and_email_from_payload(self):
        email_service = AsyncMock(spec=IEmailService)
        handler = UserCreatedWelcomeEmailHandler(email_service)
        event = UserCreatedEvent(
            payload={
                "id": str(uuid.uuid4()),
                "name": "Ana",
                "email": "ana@test.com",
                "cpf": "12345678900",
            }
        )

        await handler.handle(event)

        email_service.send.assert_called_once()
        _, kwargs = email_service.send.call_args
        assert kwargs["to"] == "ana@test.com"
        assert "Ana" in kwargs["body"]
