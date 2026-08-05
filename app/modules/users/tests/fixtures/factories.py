import bcrypt
import pytest

from app.modules.users.domain.enums.user_role import UserRole
from app.modules.users.infrastructure.persistence.users_model import UserModel

_default_hash = bcrypt.hashpw(b"Pass@123", bcrypt.gensalt()).decode()


@pytest.fixture
def user_factory(db_session, faker):
    async def make_user(
        *,
        name: str | None = None,
        email: str | None = None,
        cpf: str | None = None,
        password_hash: str = _default_hash,
        role: UserRole = UserRole.USER,
        count: int = 1,
        **kwargs,
    ):
        users = []
        for _ in range(count):
            user = UserModel(
                name=name or faker.name(),
                email=email or faker.unique.email(),
                cpf=cpf or faker.unique.numerify(text="###########"),
                password_hash=password_hash,
                role=role.value,
                **kwargs,
            )
            db_session.add(user)
            users.append(user)
        await db_session.commit()

        return users if count > 1 else users[0]

    return make_user
