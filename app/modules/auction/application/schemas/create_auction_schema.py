from pydantic import BaseModel, Field


class CreateAuctionSchema(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    user_id: str = Field(..., min_length=36, max_length=36)
    start_price: float = Field(..., ge=0)
    minimum_increment: float = Field(..., ge=0)
    status: str = Field(default="created")
    images: list[str] | None = Field(default=None)
