from datetime import UTC, datetime
from decimal import Decimal

from app.modules.auction.application.tasks.auction_tasks import (
    finish_auction_task,
    start_auction_task,
)
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import AuctionScheduledEvent
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)


class AuctionScheduledHandler:
    def __init__(self, read_repository: AuctionReadRepository):
        self.read_repository = read_repository

    async def handle(self, event: AuctionScheduledEvent) -> None:
        auction_id = str(event.payload["id"])
        start_time = datetime.fromisoformat(event.payload["start_time"])
        end_time = datetime.fromisoformat(event.payload["end_time"])
        now = datetime.now(UTC)

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=UTC)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=UTC)

        start_delay = max(0, int((start_time - now).total_seconds()))
        end_delay = max(0, int((end_time - now).total_seconds()))

        start_auction_task.apply_async(
            args=[auction_id],
            countdown=start_delay,
            task_id=f"start-{auction_id}",
        )
        finish_auction_task.apply_async(
            args=[auction_id],
            countdown=end_delay,
            task_id=f"finish-{auction_id}",
        )

        current_auction = await self.read_repository.get_by_id(auction_id)
        if not current_auction:
            return

        current_auction.status = AuctionStatus.SCHEDULED.value
        current_auction.start_time = start_time
        current_auction.end_time = end_time
        current_auction.highest_bid = Decimal(event.payload["starting_price"])
        current_auction.minimum_increment = Decimal(event.payload["minimum_increment"])
        await self.read_repository.save(current_auction)
