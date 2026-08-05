import uuid

from app.modules.auction.application.schemas.create_auction_schema import (
    CreateAuctionSchema,
)
from app.modules.auction.domain.auction_aggregate import Auction
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.ports.auction_repository_interface import (
    IAuctionRepository,
)
from app.modules.auction.domain.ports.event_bus_interface import EventBusInterface


class CreateAuctionUseCase:
    def __init__(
        self, repository: IAuctionRepository, event_bus: EventBusInterface
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, data: CreateAuctionSchema, user_id: uuid.UUID) -> Auction:
        auction = Auction.create(
            user_id=user_id,
            title=data.title,
            description=data.description or "",
            start_price=data.start_price,
            minimum_increment=data.minimum_increment,
            status=AuctionStatus(data.status),
            images=data.images,
        )
        await self._repository.save(auction)
        events = auction.pull_events()
        await self._event_bus.publish(events)
        return auction
