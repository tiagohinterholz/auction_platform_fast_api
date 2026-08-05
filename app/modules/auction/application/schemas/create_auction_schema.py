from decimal import Decimal

from pydantic import BaseModel, Field


class CreateAuctionSchema(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    start_price: Decimal = Field(..., ge=0)
    minimum_increment: Decimal = Field(..., ge=0)
    images: list[str] | None = Field(default=None)
