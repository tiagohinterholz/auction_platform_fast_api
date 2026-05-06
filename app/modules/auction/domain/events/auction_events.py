from typing import Any

from app.core.events.base_events import BaseDomainEvent


class AuctionCreatedEvent(BaseDomainEvent):
    name: str = "auction.created"
    payload: dict[str, Any]


class AuctionStartedEvent(BaseDomainEvent):
    name: str = "auction.started"
    payload: dict[str, str]


class AuctionScheduledEvent(BaseDomainEvent):
    name: str = "auction.scheduled"
    payload: dict[str, str]


class AuctionActiveEvent(BaseDomainEvent):
    name: str = "auction.active"
    payload: dict[str, str]


class AuctionExtendedEvent(BaseDomainEvent):
    name: str = "auction.extended"
    payload: dict[str, str]


class AuctionFinishedEvent(BaseDomainEvent):
    name: str = "auction.finished"
    payload: dict[str, str]


class AuctionCancelledEvent(BaseDomainEvent):
    name: str = "auction.cancelled"
    payload: dict[str, str]
    reason: str | None = None
