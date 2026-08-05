import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class AuctionReadModel(Base):
    __tablename__ = "auctions_read"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="CREATED")
    start_price: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_increment: Mapped[float] = mapped_column(Float, nullable=False)
    highest_bid: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    images: Mapped[list | None] = mapped_column(JSON, nullable=True)
