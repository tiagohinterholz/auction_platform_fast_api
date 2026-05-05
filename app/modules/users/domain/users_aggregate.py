import uuid
from typing import List, Optional

from .exceptions.users_exceptions import (
    InvalidUserEmailException,
    InvalidUserNameException,
    InvalidUserCPFException,
)
from .enums.user_role import UserRole
from .events.users_events import UserCreatedEvent, UserDeletedEvent, UserUpdatedEvent


class User:
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        email: str,
        cpf: str,
        password_hash: str,
        role: UserRole,
        is_active: bool = True,
    ):
        self._id = id
        self._name = name
        self._email = email
        self._cpf = cpf
        self._password_hash = password_hash
        self._role = role
        self._is_active = is_active
        self.events: List = []

    @classmethod
    def create(
        cls, name: str, email: str, cpf: str, password_hash: str, role: UserRole
    ) -> "User":
        if not name.strip():
            raise InvalidUserNameException()
        if "@" not in email:
            raise InvalidUserEmailException()
        if not cpf.strip() or len(cpf) != 11:
            raise InvalidUserCPFException()

        user = cls(
            id=uuid.uuid4(),
            name=name,
            email=email,
            cpf=cpf,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        user.events.append(
            UserCreatedEvent(
                payload={
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "cpf": user.cpf,
                },
            )
        )
        return user

    def update(self, name: Optional[str] = None, email: Optional[str] = None) -> None:
        if name is not None:
            self._name = name

        if email is not None:
            if "@" not in email:
                raise InvalidUserEmailException(email)
            self._email = email

        self.events.append(
            UserUpdatedEvent(
                payload={
                    "id": str(self.id),
                    "name": self.name,
                    "email": self.email,
                },
            )
        )

    def delete(self) -> None:
        self._is_active = False
        self.events.append(
            UserDeletedEvent(
                payload={
                    "id": str(self.id),
                    "name": self.name,
                    "email": self.email,
                },
            )
        )

    def pull_events(self) -> List:
        events = self.events.copy()
        self.events.clear()
        return events

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def cpf(self) -> str:
        return self._cpf

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._is_active
