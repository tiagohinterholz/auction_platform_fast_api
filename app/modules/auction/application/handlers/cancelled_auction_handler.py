from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionCancelledEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)


class AuctionCancelledHandler:
    def __init__(self, read_repository: AuctionReadRepository):
        self.read_repository = read_repository

    async def handle(self, event: AuctionCancelledEvent) -> None:
        auction_id = str(event.payload["id"])
        current_auction = await self.read_repository.get_by_id(auction_id)
        if not current_auction:
            return

        current_auction.status = AuctionStatus.CANCELLED.value
        current_auction.reason = str(event.payload["reason"])
        await self.read_repository.save(current_auction)
