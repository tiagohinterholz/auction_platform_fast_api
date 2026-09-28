import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class BidReadModel:
    id: uuid.UUID
    auction_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    timestamp: datetime