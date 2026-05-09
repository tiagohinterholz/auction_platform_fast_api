from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.bidding.domain.ports.event_bus_interface import EventBusInterface
from app.modules.bidding.infrastructure.event_bus import DummyEventBus
from app.modules.bidding.infrastructure.repository.bidding_repository import BiddingRepository
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.core.database.session import get_db
from app.modules.bidding.application.usecases.place_bid_use_case import PlaceBidUseCase
from app.core.locks.redis_lock import RedisLockService
from app.modules.auction.infrastructure.repository.auction_read_repository import AuctionReadRepository
from app.modules.auction.routers.dependencies import get_auction_read_repository
from app.core.locks.dependencies import get_lock_service


def get_bidding_repository(
    session: AsyncSession = Depends(get_db),
) -> BiddingRepository:
    return BiddingRepository(session)


def get_bid_read_repository(
    session: AsyncSession = Depends(get_db),
) -> BidReadRepository:
    return BidReadRepository(session)


def get_event_bus() -> EventBusInterface:
    return DummyEventBus()


def get_place_bid_use_case(
    bidding_repo: BiddingRepository = Depends(get_bidding_repository),
    auction_read_repo: AuctionReadRepository = Depends(get_auction_read_repository),
    bus: EventBusInterface = Depends(get_event_bus),
    lock_service: RedisLockService = Depends(get_lock_service)
) -> PlaceBidUseCase:
    return PlaceBidUseCase(bidding_repo, auction_read_repo, bus, lock_service)