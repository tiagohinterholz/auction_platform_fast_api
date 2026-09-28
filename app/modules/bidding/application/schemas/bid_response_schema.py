from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_validator


class BidResponseSchema(BaseModel):
    id: UUID
    auction_id: UUID
    user_id: UUID
    amount: Decimal
    timestamp: datetime

    model_config = {"from_attributes": True}

    @field_validator("timestamp", mode="after")
    @classmethod
    def _tag_utc(cls, value: datetime) -> datetime:
        # timestamp is never None here, unlike AuctionSchema's start/end -
        # app.core.schemas.timezone.as_utc() is typed for the optional case.
        return value if value.tzinfo else value.replace(tzinfo=UTC)
