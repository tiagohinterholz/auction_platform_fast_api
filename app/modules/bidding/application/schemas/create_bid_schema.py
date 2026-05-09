from pydantic import BaseModel, Field


class CreateBidSchema(BaseModel):
    amount: float = Field(..., gt=0)