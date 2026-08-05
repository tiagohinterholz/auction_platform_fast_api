import uuid

from sqlalchemy import UUID, Column, DateTime, Numeric

from app.core.database.base import Base


class BidReadModel(Base):
    __tablename__ = "bids_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False)