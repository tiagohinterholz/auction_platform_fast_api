from core.events.base_events import BaseDomainEvent


class BidPlacedEvent(BaseDomainEvent):
    name: str = "bid.placed"
    payload: dict[str, str | float]