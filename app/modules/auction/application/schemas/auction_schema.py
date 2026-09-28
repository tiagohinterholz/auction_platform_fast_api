import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.schemas.timezone import as_utc


class AuctionSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    status: str
    start_price: Decimal
    minimum_increment: Decimal
    highest_bid: Decimal | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    images: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_time", "end_time", mode="after")
    @classmethod
    def _tag_utc(cls, value: datetime | None) -> datetime | None:
        return as_utc(value)
