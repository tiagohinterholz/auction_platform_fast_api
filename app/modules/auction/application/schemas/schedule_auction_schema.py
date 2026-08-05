from datetime import datetime

from pydantic import BaseModel, Field


class ScheduleAuctionSchema(BaseModel):
    start_date: datetime = Field(..., description="YYYY-MM-DD HH:MM:SS")
    end_date: datetime = Field(..., description="YYYY-MM-DD HH:MM:SS")
