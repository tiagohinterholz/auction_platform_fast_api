from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.modules.auction.application.handlers.started_auction_handler import (
    AuctionStartedHandler,
)
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionStartedEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)


class TestAuctionStartedHandler:

    def setup_method(self):
        self.read_repo = AsyncMock(spec=AuctionReadRepository)
        self.handler = AuctionStartedHandler(self.read_repo)

    async def test_sets_status_to_active_and_saves(self):
        auction = SimpleNamespace(id="auction-1", status=AuctionStatus.SCHEDULED.value)
        self.read_repo.get_by_id.return_value = auction
        event = AuctionStartedEvent(
            payload={
                "id": "auction-1",
                "start_time": "",
                "end_time": "",
                "starting_price": "100.00",
                "minimum_increment": "10.00",
                "status": "active",
            }
        )

        await self.handler.handle(event)

        assert auction.status == AuctionStatus.ACTIVE.value
        self.read_repo.save.assert_called_once_with(auction)

    async def test_does_nothing_when_auction_is_not_found(self):
        self.read_repo.get_by_id.return_value = None
        event = AuctionStartedEvent(
            payload={
                "id": "missing",
                "start_time": "",
                "end_time": "",
                "starting_price": "100.00",
                "minimum_increment": "10.00",
                "status": "active",
            }
        )

        await self.handler.handle(event)

        self.read_repo.save.assert_not_called()
