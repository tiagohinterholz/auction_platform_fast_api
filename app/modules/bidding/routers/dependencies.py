from typing import Annotated

from fastapi import Depends

from app.core.database.session import SessionDep
from app.core.events.dependencies import EventBusDep
from app.core.locks.dependencies import LockServiceDep
from app.modules.auction.routers.dependencies import AuctionRepositoryDep
from app.modules.bidding.application.usecases.place_bid_use_case import PlaceBidUseCase
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.modules.bidding.infrastructure.repository.bidding_repository import BiddingRepository


def get_bidding_repository(session: SessionDep) -> BiddingRepository:
    return BiddingRepository(session)


def get_bid_read_repository(session: SessionDep) -> BidReadRepository:
    return BidReadRepository(session)


BiddingRepositoryDep = Annotated[BiddingRepository, Depends(get_bidding_repository)]
BidReadRepositoryDep = Annotated[BidReadRepository, Depends(get_bid_read_repository)]


def get_place_bid_use_case(
    bidding_repo: BiddingRepositoryDep,
    auction_repo: AuctionRepositoryDep,
    bus: EventBusDep,
    lock_service: LockServiceDep,
) -> PlaceBidUseCase:
    return PlaceBidUseCase(bidding_repo, auction_repo, bus, lock_service)


PlaceBidUseCaseDep = Annotated[PlaceBidUseCase, Depends(get_place_bid_use_case)]
