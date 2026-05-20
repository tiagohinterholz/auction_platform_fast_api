from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import get_db
from app.core.events.event_bus_interface import EventBusInterface
from app.modules.auction.infrastructure.repository.auction_repository import (
    AuctionRepository,
)
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)

from app.modules.auction.application.usecases.create_auction_use_case import (
    CreateAuctionUseCase,
)
from app.modules.auction.application.usecases.schedule_auction_use_case import (
    ScheduleAuctionUseCase,
)
from app.modules.auction.application.usecases.cancel_auction_use_case import (
    CancelAuctionUseCase,
)


def get_auction_repository(
    session: AsyncSession = Depends(get_db),
) -> AuctionRepository:
    return AuctionRepository(session)


def get_auction_read_repository(
    session: AsyncSession = Depends(get_db),
) -> AuctionReadRepository:
    return AuctionReadRepository(session)


def get_event_bus(request: Request) -> EventBusInterface:
    return request.app.state.event_bus


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
