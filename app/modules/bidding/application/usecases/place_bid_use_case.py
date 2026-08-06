from decimal import Decimal
from uuid import UUID

from app.core.locks.lock_interface import ILockService
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.exceptions.auction_exceptions import AuctionNotFoundException
from app.modules.auction.domain.ports.auction_repository_interface import IAuctionRepository
from app.modules.bidding.domain.bidding_aggregate import Bidding
from app.modules.bidding.domain.exceptions.bidding_exceptions import (
    AuctionBeingProcessedException,
    InvalidBidPlaceException,
)
from app.modules.bidding.domain.ports.bidding_repository_interface import IBiddingRepository
from app.modules.bidding.domain.ports.event_bus_interface import EventBusInterface

# Generous margin over the critical section's real cost (a couple of DB
# round trips) so a slow-but-alive request never loses its lock mid-flight
# to another bidder on the same auction.
BID_LOCK_TTL_MS = 8000


class PlaceBidUseCase:
    def __init__(
        self, 
        bidding_repository: IBiddingRepository, 
        auction_repository: IAuctionRepository, 
        event_bus: EventBusInterface, 
        lock_manager: ILockService
    ):
        self.bidding_repository = bidding_repository
        self.auction_repository = auction_repository
        self.event_bus = event_bus
        self.lock_manager = lock_manager
    
    async def execute(self, auction_id: UUID, user_id: UUID, amount: Decimal) -> None:
        lock_acquired = False
        try:
            lock_acquired = await self.lock_manager.acquire(
                f'auction:{auction_id}:lock', BID_LOCK_TTL_MS
            )
            if not lock_acquired:
                raise AuctionBeingProcessedException()

            auction = await self.auction_repository.get_by_id(str(auction_id))
            if not auction:
                raise AuctionNotFoundException(f"Auction with id {auction_id} not found.")
            
            if auction.status != AuctionStatus.ACTIVE:
                raise InvalidBidPlaceException("Cannot place a bid on an inactive auction.")
            
            bidding = await self.bidding_repository.find_by_auction_id(str(auction_id))
            if not bidding:
                bidding = Bidding.open(
                    auction_id=auction_id, 
                    starting_price=auction.start_price,
                    minimum_increment=auction.minimum_increment
                )
            bidding.place_bid(user_id, amount)
            await self.bidding_repository.save(bidding)
            await self.event_bus.publish(bidding.pull_events())
        finally:
            if lock_acquired:
                await self.lock_manager.release(f'auction:{auction_id}:lock')