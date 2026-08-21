from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.modules.auction.application.handlers.scheduled_auction_handler import (
    AuctionScheduledHandler,
)
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionScheduledEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)

HANDLER_MODULE = "app.modules.auction.application.handlers.scheduled_auction_handler"


class TestAuctionScheduledHandler:

    def setup_method(self):
        self.read_repo = AsyncMock(spec=AuctionReadRepository)
        self.handler = AuctionScheduledHandler(self.read_repo)

    def _event(self) -> AuctionScheduledEvent:
        now = datetime.now(UTC)
        return AuctionScheduledEvent(
            payload={
                "id": "auction-1",
                "start_time": (now + timedelta(hours=1)).isoformat(),
                "end_time": (now + timedelta(hours=3)).isoformat(),
                "starting_price": "100.00",
                "minimum_increment": "10.00",
            }
        )

    @patch(f"{HANDLER_MODULE}.finish_auction_task")
    @patch(f"{HANDLER_MODULE}.start_auction_task")
    async def test_schedules_both_celery_tasks_and_updates_read_model(
        self, start_task, finish_task
    ):
        auction = SimpleNamespace(
            id="auction-1",
            status=AuctionStatus.CREATED.value,
            start_time=None,
            end_time=None,
            highest_bid=None,
            minimum_increment=None,
        )
        self.read_repo.get_by_id.return_value = auction

        await self.handler.handle(self._event())

        start_task.apply_async.assert_called_once()
        assert start_task.apply_async.call_args.kwargs["task_id"] == "start-auction-1"
        finish_task.apply_async.assert_called_once()
        assert finish_task.apply_async.call_args.kwargs["task_id"] == "finish-auction-1"

        assert auction.status == AuctionStatus.SCHEDULED.value
        assert auction.highest_bid == Decimal("100.00")
        assert auction.minimum_increment == Decimal("10.00")
        self.read_repo.save.assert_called_once_with(auction)

    @patch(f"{HANDLER_MODULE}.finish_auction_task")
    @patch(f"{HANDLER_MODULE}.start_auction_task")
    async def test_still_schedules_tasks_even_when_read_model_is_missing(
        self, start_task, finish_task
    ):
        self.read_repo.get_by_id.return_value = None

        await self.handler.handle(self._event())

        start_task.apply_async.assert_called_once()
        finish_task.apply_async.assert_called_once()
        self.read_repo.save.assert_not_called()
