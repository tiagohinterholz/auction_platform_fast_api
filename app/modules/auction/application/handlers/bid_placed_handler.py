from datetime import datetime

from app.modules.bidding.domain.events.bid_events import BidPlacedEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import AuctionReadRepository
from app.modules.auction.infrastructure.repository.auction_repository import AuctionRepository
from app.core.events.event_bus_interface import EventBusInterface


class BidPlacedHandler:
    def __init__(
        self,
        write_repository: AuctionRepository,
        read_repository: AuctionReadRepository,
        event_bus: EventBusInterface,
    ):
        self.write_repository = write_repository
        self.read_repository = read_repository
        self.event_bus = event_bus

    async def handle(self, event: BidPlacedEvent) -> None:
        auction_id = str(event.payload["auction_id"])

        auction = await self.write_repository.get_by_id(auction_id)
        if not auction:
            return

        auction.apply_anti_sniping(datetime.now())
        await self.write_repository.save(auction)

        current_auction = await self.read_repository.get_by_id(auction_id)
        if current_auction:
            current_auction.highest_bid = float(event.payload["amount"])
            current_auction.end_time = auction.end_time
            await self.read_repository.save(current_auction)

        await self.event_bus.publish(auction.pull_events())
