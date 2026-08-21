from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.modules.auction.application.handlers.cancelled_auction_handler import (
    AuctionCancelledHandler,
)
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionCancelledEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)


class TestAuctionCancelledHandler:

    def setup_method(self):
        self.read_repo = AsyncMock(spec=AuctionReadRepository)
        self.handler = AuctionCancelledHandler(self.read_repo)

    async def test_sets_status_to_cancelled_with_reason_and_saves(self):
        auction = SimpleNamespace(id="auction-1", status=AuctionStatus.CREATED.value, reason=None)
        self.read_repo.get_by_id.return_value = auction
        event = AuctionCancelledEvent(
            payload={"id": "auction-1", "cancelled_at": "", "reason": "Mudei de ideia"}
        )

        await self.handler.handle(event)

        assert auction.status == AuctionStatus.CANCELLED.value
        assert auction.reason == "Mudei de ideia"
        self.read_repo.save.assert_called_once_with(auction)

    async def test_does_nothing_when_auction_is_not_found(self):
        self.read_repo.get_by_id.return_value = None
        event = AuctionCancelledEvent(payload={"id": "missing", "cancelled_at": "", "reason": ""})

        await self.handler.handle(event)

        self.read_repo.save.assert_not_called()
