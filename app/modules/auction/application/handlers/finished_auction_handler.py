from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionFinishedEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)


class AuctionFinishedHandler:
    def __init__(self, read_repository: AuctionReadRepository):
        self.read_repository = read_repository

    async def handle(self, event: AuctionFinishedEvent) -> None:
        auction_id = str(event.payload["id"])
        current_auction = await self.read_repository.get_by_id(auction_id)
        if not current_auction:
            return

        current_auction.status = AuctionStatus.FINISHED.value
        await self.read_repository.save(current_auction)
