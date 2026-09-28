import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.modules.bidding.domain.events.bid_events import BidPlacedEvent
from app.modules.bidding.domain.ports.bidding_read_repository_interface import IBidReadRepository
from app.modules.bidding.domain.read_models.bid_read_model import BidReadModel


class BidPlacedHandler:
    def __init__(self, read_repository: IBidReadRepository):
        self.read_repository = read_repository

    async def handle(self, event: BidPlacedEvent) -> None:
        model = BidReadModel(
            id=uuid.uuid4(),
            auction_id=uuid.UUID(str(event.payload["auction_id"])),
            user_id=uuid.UUID(str(event.payload["user_id"])),
            amount=Decimal(event.payload["amount"]),
            # Column is TIMESTAMP WITHOUT TIME ZONE - store naive, computed
            # from UTC rather than the server's local time.
            timestamp=datetime.now(UTC).replace(tzinfo=None),
        )
        await self.read_repository.save(model)
