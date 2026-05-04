from pydantic import BaseModel, Field


class CancelAuctionSchema(BaseModel):
    reason: str = Field(..., min_length=1, max_length=200)
