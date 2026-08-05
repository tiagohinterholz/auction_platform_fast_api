import uuid
from datetime import datetime
from decimal import Decimal

from app.modules.bidding.domain.events.bid_events import BidPlacedEvent
from app.modules.bidding.infrastructure.persistence.bid_read_model import BidReadModel
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository


class BidPlacedHandler:
    def __init__(self, read_repository: BidReadRepository):
        self.read_repository = read_repository

    async def handle(self, event: BidPlacedEvent) -> None:
        model = BidReadModel(
            id=uuid.uuid4(),
            auction_id=uuid.UUID(str(event.payload["auction_id"])),
            user_id=uuid.UUID(str(event.payload["user_id"])),
            amount=Decimal(event.payload["amount"]),
            timestamp=datetime.now(),
        )
        await self.read_repository.save(model)
