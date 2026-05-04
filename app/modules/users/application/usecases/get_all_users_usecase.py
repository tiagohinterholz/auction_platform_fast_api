from app.modules.users.domain.users_aggregate import User
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository


class GetAllUsersUseCase:
    def __init__(self, repository: IUsersRepository) -> None:
        self.repository = repository

    async def execute(self) -> list[User]:
        users = await self.repository.get_all()

        if not users:
            return []

        return users
