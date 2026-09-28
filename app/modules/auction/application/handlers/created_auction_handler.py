from decimal import Decimal

from app.modules.auction.domain.events.auction_events import AuctionCreatedEvent
from app.modules.auction.domain.ports.auction_read_repository_interface import (
    IAuctionReadRepository,
)
from app.modules.auction.domain.read_models.auction_read_model import AuctionReadModel


class AuctionCreatedHandler:
    def __init__(self, read_repository: IAuctionReadRepository):
        self.read_repository = read_repository

    async def handle(self, event: AuctionCreatedEvent) -> None:
        auction = AuctionReadModel(
            id=event.payload["id"],
            user_id=event.payload["user_id"],
            title=event.payload["title"],
            description=event.payload["description"],
            start_price=Decimal(event.payload["start_price"]),
            start_time=None,
            end_time=None,
            highest_bid=None,
            minimum_increment=Decimal(event.payload["minimum_increment"]),
            reason=None,
            status=event.payload["status"],
            images=event.payload["images"],
        )
        await self.read_repository.save(auction)
