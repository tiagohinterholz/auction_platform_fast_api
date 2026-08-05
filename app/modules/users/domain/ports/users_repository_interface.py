from abc import ABC, abstractmethod

from app.modules.users.domain.users_aggregate import User


class IUsersRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> User:
        pass

    @abstractmethod
    async def get_by_cpf(self, cpf: str) -> User:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
        pass
