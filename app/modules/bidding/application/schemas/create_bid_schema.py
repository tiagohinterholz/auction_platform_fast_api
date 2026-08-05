from decimal import Decimal

from pydantic import BaseModel, Field


class CreateBidSchema(BaseModel):
    amount: Decimal = Field(..., gt=0)
