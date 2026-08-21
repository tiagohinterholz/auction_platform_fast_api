import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class BidReadModel(Base):
    __tablename__ = "bids_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    auction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)