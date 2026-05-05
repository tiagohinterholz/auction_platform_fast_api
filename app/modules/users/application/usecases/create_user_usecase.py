from app.modules.users.application.schemas.create_user_schema import CreateUserSchema
from app.modules.users.domain.users_aggregate import User
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.domain.enums import UserRole


class CreateUserUseCase:
    def __init__(self, repository: IUsersRepository) -> None:
        self.repository = repository

    async def execute(self, data: CreateUserSchema) -> User:

        user = User.create(
            name=data.name,
            email=data.email,
            cpf=data.cpf,
            password_hash=data.password,
            role=UserRole.USER,
        )
        await self.repository.save(user)
        return user
