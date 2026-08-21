from app.core.events.event_bus_interface import EventBusInterface
from app.modules.users.application.schemas.update_user_schema import UpdateUserSchema
from app.modules.users.domain.exceptions.users_exceptions import UserNotFoundException
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.domain.users_aggregate import User


class UpdateUserUseCase:
    def __init__(self, repository: IUsersRepository, event_bus: EventBusInterface) -> None:
        self.repository = repository
        self.event_bus = event_bus

    async def execute(self, user_id: str, data: UpdateUserSchema) -> User:
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id)

        user.update(name=data.name, email=data.email)
        await self.repository.save(user)
        await self.event_bus.publish(user.pull_events())

        return user
