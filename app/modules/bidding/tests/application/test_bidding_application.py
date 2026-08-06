import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.events.event_bus_interface import EventBusInterface
from app.core.locks.lock_interface import ILockService
from app.modules.auction.domain.auction_aggregate import Auction
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.exceptions.auction_exceptions import AuctionNotFoundException
from app.modules.auction.domain.ports.auction_repository_interface import IAuctionRepository
from app.modules.bidding.application.usecases.place_bid_use_case import PlaceBidUseCase
from app.modules.bidding.domain.exceptions.bidding_exceptions import (
    AuctionBeingProcessedException,
    InvalidBidPlaceException,
)
from app.modules.bidding.domain.ports.bidding_repository_interface import IBiddingRepository


def _make_auction(status: AuctionStatus) -> Auction:
    return Auction.restore(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Leilão teste",
        description="Descrição válida",
        start_price=Decimal("100.0"),
        minimum_increment=Decimal("10.0"),
        status=status,
        images=[],
    )


class TestBiddingApplication:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.bidding_repo = AsyncMock(spec=IBiddingRepository)
        self.auction_repo = AsyncMock(spec=IAuctionRepository)
        self.event_bus = AsyncMock(spec=EventBusInterface)
        self.lock = AsyncMock(spec=ILockService)
        self.use_case = PlaceBidUseCase(
            bidding_repository=self.bidding_repo,
            auction_repository=self.auction_repo,
            event_bus=self.event_bus,
            lock_manager=self.lock,
        )

    async def test_place_bid_calls_save(self, user_obj):
        auction = _make_auction(AuctionStatus.ACTIVE)
        self.lock.acquire.return_value = True
        self.auction_repo.get_by_id.return_value = auction
        self.bidding_repo.find_by_auction_id.return_value = None

        await self.use_case.execute(auction.id, user_obj.id, Decimal("150.0"))

        self.bidding_repo.save.assert_called_once()

    async def test_place_bid_fails_when_lock_not_acquired(self, user_obj):
        self.lock.acquire.return_value = False

        with pytest.raises(AuctionBeingProcessedException):
            await self.use_case.execute(uuid.uuid4(), user_obj.id, Decimal("150.0"))

        self.bidding_repo.save.assert_not_called()

    async def test_place_bid_auction_not_found(self, user_obj):
        self.lock.acquire.return_value = True
        self.auction_repo.get_by_id.return_value = None

        with pytest.raises(AuctionNotFoundException):
            await self.use_case.execute(uuid.uuid4(), user_obj.id, Decimal("150.0"))

        self.bidding_repo.save.assert_not_called()

    async def test_place_bid_auction_not_active(self, user_obj):
        auction = _make_auction(AuctionStatus.CREATED)
        self.lock.acquire.return_value = True
        self.auction_repo.get_by_id.return_value = auction

        with pytest.raises(InvalidBidPlaceException):
            await self.use_case.execute(auction.id, user_obj.id, Decimal("150.0"))

        self.bidding_repo.save.assert_not_called()
