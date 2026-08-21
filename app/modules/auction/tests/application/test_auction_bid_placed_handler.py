import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.core.events.event_bus_interface import EventBusInterface
from app.modules.auction.application.handlers.bid_placed_handler import BidPlacedHandler
from app.modules.auction.domain.auction_aggregate import Auction
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionExtendedEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)
from app.modules.auction.infrastructure.repository.auction_repository import AuctionRepository
from app.modules.bidding.domain.events.bid_events import BidPlacedEvent


def _make_active_auction(end_time: datetime) -> Auction:
    return Auction.restore(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="iPhone 15",
        description="desc",
        start_price=Decimal("100.00"),
        minimum_increment=Decimal("10.00"),
        status=AuctionStatus.ACTIVE,
        images=[],
        start_time=datetime.now() - timedelta(hours=1),
        end_time=end_time,
    )


class TestAuctionBidPlacedHandler:

    def setup_method(self):
        self.write_repo = AsyncMock(spec=AuctionRepository)
        self.read_repo = AsyncMock(spec=AuctionReadRepository)
        self.event_bus = AsyncMock(spec=EventBusInterface)
        self.handler = BidPlacedHandler(self.write_repo, self.read_repo, self.event_bus)

    def _event(self, auction_id: uuid.UUID, amount: str = "150.00") -> BidPlacedEvent:
        return BidPlacedEvent(
            payload={"auction_id": str(auction_id), "user_id": str(uuid.uuid4()), "amount": amount}
        )

    async def test_updates_highest_bid_on_the_read_model(self):
        auction = _make_active_auction(end_time=datetime.now() + timedelta(hours=1))
        self.write_repo.get_by_id.return_value = auction
        read_model = SimpleNamespace(highest_bid=None, end_time=None)
        self.read_repo.get_by_id.return_value = read_model

        await self.handler.handle(self._event(auction.id, "150.00"))

        self.write_repo.save.assert_called_once_with(auction)
        assert read_model.highest_bid == Decimal("150.00")
        assert read_model.end_time == auction.end_time
        self.read_repo.save.assert_called_once_with(read_model)
        self.event_bus.publish.assert_called_once()

    async def test_extends_end_time_and_publishes_extended_event_near_the_deadline(self):
        auction = _make_active_auction(end_time=datetime.now() + timedelta(seconds=10))
        self.write_repo.get_by_id.return_value = auction
        self.read_repo.get_by_id.return_value = SimpleNamespace(highest_bid=None, end_time=None)

        await self.handler.handle(self._event(auction.id))

        published = self.event_bus.publish.call_args.args[0]
        assert any(isinstance(e, AuctionExtendedEvent) for e in published)

    async def test_does_nothing_when_auction_is_not_found(self):
        self.write_repo.get_by_id.return_value = None

        await self.handler.handle(self._event(uuid.uuid4()))

        self.write_repo.save.assert_not_called()
        self.read_repo.save.assert_not_called()
        self.event_bus.publish.assert_not_called()
