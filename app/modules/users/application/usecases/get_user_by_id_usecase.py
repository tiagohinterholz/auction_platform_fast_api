from app.modules.users.domain.exceptions.users_exceptions import UserNotFoundException
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.domain.users_aggregate import User


class GetUserByIdUseCase:
    def __init__(self, repository: IUsersRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: str) -> User:
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id)

        return user
