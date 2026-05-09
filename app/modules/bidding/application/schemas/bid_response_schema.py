from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class BidResponseSchema(BaseModel):
    id: UUID
    auction_id: UUID
    user_id: UUID
    amount: float
    timestamp: datetime

    model_config = {"from_attributes": True}
