import pytest

from app.modules.users.domain.enums.user_role import UserRole


@pytest.fixture
async def user_obj(user_factory):
    return await user_factory()


@pytest.fixture
async def user_obj_admin(user_factory):
    return await user_factory(role=UserRole.ADMIN)
