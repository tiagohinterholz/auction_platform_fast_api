from app.modules.users.application.schemas.update_user_schema import UpdateUserSchema
from app.modules.users.domain.users_aggregate import User
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.domain.exceptions.users_exceptions import UserNotFoundException


class UpdateUserUseCase:
    def __init__(self, repository: IUsersRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: str, data: UpdateUserSchema) -> User:
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(user_id)

        user.update(name=data.name, email=data.email)
        await self.repository.save(user)

        return user
