from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.modules.auction.application.handlers.finished_auction_handler import (
    AuctionFinishedHandler,
)
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionFinishedEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)


class TestAuctionFinishedHandler:

    def setup_method(self):
        self.read_repo = AsyncMock(spec=AuctionReadRepository)
        self.handler = AuctionFinishedHandler(self.read_repo)

    async def test_sets_status_to_finished_and_saves(self):
        auction = SimpleNamespace(id="auction-1", status=AuctionStatus.ACTIVE.value)
        self.read_repo.get_by_id.return_value = auction
        event = AuctionFinishedEvent(payload={"id": "auction-1", "title": "x", "end_time": ""})

        await self.handler.handle(event)

        assert auction.status == AuctionStatus.FINISHED.value
        self.read_repo.save.assert_called_once_with(auction)

    async def test_does_nothing_when_auction_is_not_found(self):
        self.read_repo.get_by_id.return_value = None
        event = AuctionFinishedEvent(payload={"id": "missing", "title": "x", "end_time": ""})

        await self.handler.handle(event)

        self.read_repo.save.assert_not_called()
