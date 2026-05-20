from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
import uuid

class AuctionSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    status: str
    start_price: float
    minimum_increment: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    images: List[str] | None = None

    model_config = ConfigDict(from_attributes=True)
