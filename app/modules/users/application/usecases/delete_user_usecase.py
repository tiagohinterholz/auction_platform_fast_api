from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.domain.exceptions.users_exceptions import UserNotFoundException


class DeleteUserUseCase:
    def __init__(self, repository: IUsersRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: str) -> None:
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id)

        await self.repository.delete(user)

        return None
