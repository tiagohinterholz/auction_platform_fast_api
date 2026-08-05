import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID

from app.core.database.base import Base


class BiddingModel(Base):
    __tablename__ = "bidding"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), nullable=False)
    current_price = Column(Float, nullable=False)
    minimum_increment = Column(Float, nullable=False)
    last_user_id = Column(UUID(as_uuid=True), nullable=True)
    last_amount = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(UTC))

    