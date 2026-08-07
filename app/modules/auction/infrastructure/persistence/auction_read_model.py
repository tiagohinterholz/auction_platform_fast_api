import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class AuctionReadModel(Base):
    __tablename__ = "auctions_read"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="created")
    start_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    minimum_increment: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    highest_bid: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    images: Mapped[list | None] = mapped_column(JSON, nullable=True)
