import uuid

from sqlalchemy import JSON, Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database.base import Base


class AuctionModel(Base):
    __tablename__ = "auctions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    description = Column(String(255), nullable=False)
    title = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="created")
    start_price = Column(Numeric(12, 2), nullable=False)
    minimum_increment = Column(Numeric(12, 2), nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    reason = Column(String(255), nullable=True)
    images = Column(JSON, nullable=True)
