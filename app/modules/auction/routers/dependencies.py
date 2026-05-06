from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_db
from app.modules.auction.infrastructure.repository.auction_repository import (
    AuctionRepository,
)
from app.modules.auction.infrastructure.event_bus import DummyEventBus
from app.modules.auction.domain.ports.event_bus_interface import EventBusInterface

# Use Cases
from app.modules.auction.application.usecases.create_auction_use_case import (
    CreateAuctionUseCase,
)
from app.modules.auction.application.usecases.schedule_auction_use_case import (
    ScheduleAuctionUseCase,
)
from app.modules.auction.application.usecases.cancel_auction_use_case import (
    CancelAuctionUseCase,
)
from app.modules.auction.application.usecases.finish_auction_use_case import (
    FinishAuctionUseCase,
)


def get_auction_repository(
    session: AsyncSession = Depends(get_db),
) -> AuctionRepository:
    return AuctionRepository(session)


def get_event_bus() -> EventBusInterface:
    return DummyEventBus()


def get_create_auction_use_case(
    repo: AuctionRepository = Depends(get_auction_repository),
    bus: EventBusInterface = Depends(get_event_bus),
) -> CreateAuctionUseCase:
    return CreateAuctionUseCase(repo, bus)


def get_schedule_auction_use_case(
    repo: AuctionRepository = Depends(get_auction_repository),
    bus: EventBusInterface = Depends(get_event_bus),
) -> ScheduleAuctionUseCase:
    return ScheduleAuctionUseCase(repo, bus)


def get_cancel_auction_use_case(
    repo: AuctionRepository = Depends(get_auction_repository),
    bus: EventBusInterface = Depends(get_event_bus),
) -> CancelAuctionUseCase:
    return CancelAuctionUseCase(repo, bus)


def get_finish_auction_use_case(
    repo: AuctionRepository = Depends(get_auction_repository),
    bus: EventBusInterface = Depends(get_event_bus),
) -> FinishAuctionUseCase:
    return FinishAuctionUseCase(repo, bus)
