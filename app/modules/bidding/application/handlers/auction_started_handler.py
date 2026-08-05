import uuid
from decimal import Decimal

from app.modules.auction.domain.events.auction_events import AuctionStartedEvent
from app.modules.bidding.domain.bidding_aggregate import Bidding
from app.modules.bidding.domain.ports.bidding_repository_interface import IBiddingRepository


class AuctionStartedHandler:
    def __init__(self, bidding_repository: IBiddingRepository):
        self.bidding_repository = bidding_repository


    async def handle(self, event: AuctionStartedEvent) -> None:
        bidding = Bidding.open(
            auction_id=uuid.UUID(str(event.payload["id"])),
            starting_price=Decimal(event.payload["starting_price"]),
            minimum_increment=Decimal(event.payload["minimum_increment"]),
        )
        
        await self.bidding_repository.save(bidding)