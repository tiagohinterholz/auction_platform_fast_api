from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.core.events.dependencies import get_event_bus
from app.core.events.event_bus_interface import EventBusInterface
from app.core.locks.dependencies import get_lock_service
from app.core.locks.redis_lock import RedisLockService
from app.modules.auction.infrastructure.repository.auction_repository import AuctionRepository
from app.modules.auction.routers.dependencies import get_auction_repository
from app.modules.bidding.application.usecases.place_bid_use_case import PlaceBidUseCase
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.modules.bidding.infrastructure.repository.bidding_repository import BiddingRepository


def get_bidding_repository(
    session: AsyncSession = Depends(get_db),
) -> BiddingRepository:
    return BiddingRepository(session)


def get_bid_read_repository(
    session: AsyncSession = Depends(get_db),
) -> BidReadRepository:
    return BidReadRepository(session)

def get_place_bid_use_case(
    bidding_repo: BiddingRepository = Depends(get_bidding_repository),
    auction_repo: AuctionRepository = Depends(get_auction_repository),
    bus: EventBusInterface = Depends(get_event_bus),
    lock_service: RedisLockService = Depends(get_lock_service)
) -> PlaceBidUseCase:
    return PlaceBidUseCase(bidding_repo, auction_repo, bus, lock_service)