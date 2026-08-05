from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BidResponseSchema(BaseModel):
    id: UUID
    auction_id: UUID
    user_id: UUID
    amount: Decimal
    timestamp: datetime

    model_config = {"from_attributes": True}
