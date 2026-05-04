from app.core.events.base_events import BaseDomainEvent


class UserCreatedEvent(BaseDomainEvent):
    name: str = "user.created"
    payload: dict[str, str]


class UserUpdatedEvent(BaseDomainEvent):
    name: str = "user.updated"
    payload: dict[str, str]


class UserDeletedEvent(BaseDomainEvent):
    name: str = "user.deleted"
    payload: dict[str, str]
