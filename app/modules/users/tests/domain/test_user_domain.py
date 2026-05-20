import pytest

from app.modules.users.domain.users_aggregate import User
from app.modules.users.domain.enums.user_role import UserRole
from app.modules.users.domain.events.users_events import UserCreatedEvent, UserUpdatedEvent, UserDeletedEvent
from app.modules.users.domain.exceptions.users_exceptions import (
    InvalidUserNameException,
    InvalidUserEmailException,
    InvalidUserCPFException,
)


def _base_create_kwargs(**overrides):
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "cpf": "12345678901",
        "password_hash": "hashed_password",
        "role": UserRole.USER,
        **overrides,
    }


class TestUserAggregate:

    @pytest.mark.parametrize(
        "kwargs, expected_exception",
        [
            (_base_create_kwargs(), None),
            (_base_create_kwargs(name="   "), InvalidUserNameException),
            (_base_create_kwargs(email="invalidemail"), InvalidUserEmailException),
            (_base_create_kwargs(cpf="123"), InvalidUserCPFException),
            (_base_create_kwargs(cpf="   "), InvalidUserCPFException),
        ],
        ids=["valid", "empty_name", "invalid_email", "short_cpf", "blank_cpf"],
    )
    def test_user_create(self, kwargs, expected_exception):
        if expected_exception:
            with pytest.raises(expected_exception):
                User.create(**kwargs)
        else:
            user = User.create(**kwargs)
            assert user.name == kwargs["name"]
            assert user.email == kwargs["email"]
            assert user.is_active is True
            assert len(user.events) == 1
            assert isinstance(user.events[0], UserCreatedEvent)

    def test_user_update(self):
        user = User.create(**_base_create_kwargs())
        user.update(name="Jane Doe", email="jane.doe@example.com")

        assert user.name == "Jane Doe"
        assert user.email == "jane.doe@example.com"
        assert any(isinstance(e, UserUpdatedEvent) for e in user.events)

    def test_user_update_raises_on_invalid_email(self):
        user = User.create(**_base_create_kwargs())

        with pytest.raises(InvalidUserEmailException):
            user.update(email="invalidemail")

    def test_user_delete(self):
        user = User.create(**_base_create_kwargs())
        user.delete()

        assert user.is_active is False
        assert any(isinstance(e, UserDeletedEvent) for e in user.events)
