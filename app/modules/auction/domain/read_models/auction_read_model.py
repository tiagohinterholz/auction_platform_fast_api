import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class AuctionReadModel:
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    status: str
    start_price: Decimal
    minimum_increment: Decimal
    highest_bid: Decimal | None
    start_time: datetime | None
    end_time: datetime | None
    images: list[str] | None
