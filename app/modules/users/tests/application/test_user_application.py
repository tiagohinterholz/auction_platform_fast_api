import uuid
from unittest.mock import AsyncMock

import pytest

from app.core.events.event_bus_interface import EventBusInterface
from app.modules.users.application.schemas.update_user_schema import UpdateUserSchema
from app.modules.users.application.usecases.delete_user_usecase import DeleteUserUseCase
from app.modules.users.application.usecases.get_all_users_usecase import GetAllUsersUseCase
from app.modules.users.application.usecases.get_user_by_id_usecase import GetUserByIdUseCase
from app.modules.users.application.usecases.update_user_usecase import UpdateUserUseCase
from app.modules.users.domain.enums.user_role import UserRole
from app.modules.users.domain.exceptions.users_exceptions import UserNotFoundException
from app.modules.users.domain.ports.users_repository_interface import IUsersRepository
from app.modules.users.domain.users_aggregate import User


def _make_user() -> User:
    return User.restore(
        id=uuid.uuid4(),
        name="John Doe",
        email="john.doe@example.com",
        cpf="12345678901",
        password_hash="hashed_password",
        role=UserRole.USER,
    )


class UserUseCaseBase:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock(spec=IUsersRepository)


class TestGetAllUsersUseCase(UserUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.use_case = GetAllUsersUseCase(self.repo)

    async def test_returns_list_of_users(self):
        user = _make_user()
        self.repo.get_all.return_value = [user]

        result = await self.use_case.execute()

        assert result == [user]

    async def test_returns_empty_list_when_none(self):
        self.repo.get_all.return_value = None

        result = await self.use_case.execute()

        assert result == []


class TestGetUserByIdUseCase(UserUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.use_case = GetUserByIdUseCase(self.repo)

    async def test_returns_user(self):
        user = _make_user()
        self.repo.get_by_id.return_value = user

        result = await self.use_case.execute(str(user.id))

        assert result == user

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundException):
            await self.use_case.execute(str(uuid.uuid4()))


class TestUpdateUserUseCase(UserUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.event_bus = AsyncMock(spec=EventBusInterface)
        self.use_case = UpdateUserUseCase(self.repo, self.event_bus)

    async def test_updates_and_saves(self):
        user = _make_user()
        self.repo.get_by_id.return_value = user

        data = UpdateUserSchema(name="Jane Doe", email="jane.doe@example.com")
        result = await self.use_case.execute(str(user.id), data)

        self.repo.save.assert_called_once()
        assert result.name == "Jane Doe"
        assert result.email == "jane.doe@example.com"
        self.event_bus.publish.assert_called_once()

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundException):
            await self.use_case.execute(str(uuid.uuid4()), UpdateUserSchema(name="Jane"))


class TestDeleteUserUseCase(UserUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.event_bus = AsyncMock(spec=EventBusInterface)
        self.use_case = DeleteUserUseCase(self.repo, self.event_bus)

    async def test_saves_user(self):
        user = _make_user()
        self.repo.get_by_id.return_value = user

        result = await self.use_case.execute(str(user.id))

        self.repo.save.assert_called_once()
        assert user.is_active is False
        assert result is None
        self.event_bus.publish.assert_called_once()

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundException):
            await self.use_case.execute(str(uuid.uuid4()))
