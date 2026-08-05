import uuid
from datetime import datetime

from app.modules.auction.domain.auction_aggregate import Auction
from app.modules.auction.domain.exceptions.auction_exceptions import (
    InvalidAuctionIdException,
)
from app.modules.auction.domain.ports.auction_repository_interface import (
    IAuctionRepository,
)
from app.modules.auction.domain.ports.event_bus_interface import EventBusInterface


class CancelAuctionUseCase:
    def __init__(
        self, repository: IAuctionRepository, event_bus: EventBusInterface
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def execute(
        self, id: uuid.UUID, current_date: datetime, reason: str | None = None
    ) -> Auction:
        auction = await self._repository.get_by_id(str(id))
        if not auction:
            raise InvalidAuctionIdException(f"Auction with id {id} not found.")

        auction.cancel(current_date, reason)
        await self._repository.save(auction)
        events = auction.pull_events()
        await self._event_bus.publish(events)
        return auction
