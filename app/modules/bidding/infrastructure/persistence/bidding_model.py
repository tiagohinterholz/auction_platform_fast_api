import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID

from app.core.database.base import Base


class BiddingModel(Base):
    __tablename__ = "bidding"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=False)
    minimum_increment = Column(Numeric(12, 2), nullable=False)
    last_user_id = Column(UUID(as_uuid=True), nullable=True)
    last_amount = Column(Numeric(12, 2), nullable=True)
    timestamp = Column(DateTime, default=datetime.now(UTC))

    