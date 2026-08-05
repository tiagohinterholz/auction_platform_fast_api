from decimal import Decimal

from app.modules.auction.domain.events.auction_events import AuctionCreatedEvent
from app.modules.auction.infrastructure.persistence.auction_read_model import AuctionReadModel
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)


class AuctionCreatedHandler:
    def __init__(self, read_repository: AuctionReadRepository):
        self.read_repository = read_repository

    async def handle(self, event: AuctionCreatedEvent) -> None:
        auction = AuctionReadModel(
            id=event.payload["id"],
            user_id=event.payload["user_id"],
            title=event.payload["title"],
            description=event.payload["description"],
            start_price=Decimal(event.payload["start_price"]),
            minimum_increment=Decimal(event.payload["minimum_increment"]),
            images=event.payload["images"],
        )
        await self.read_repository.save(auction)
