from app.core.events.event_bus_interface import EventBusInterface
from app.modules.users.domain.exceptions.users_exceptions import UserNotFoundException
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository


class DeleteUserUseCase:
    def __init__(self, repository: IUsersRepository, event_bus: EventBusInterface) -> None:
        self.repository = repository
        self.event_bus = event_bus

    async def execute(self, user_id: str) -> None:
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id)

        user.delete()
        await self.repository.save(user)
        await self.event_bus.publish(user.pull_events())

        return
