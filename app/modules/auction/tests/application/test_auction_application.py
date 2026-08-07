import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.events.event_bus_interface import EventBusInterface
from app.modules.auction.application.schemas.create_auction_schema import CreateAuctionSchema
from app.modules.auction.application.schemas.schedule_auction_schema import ScheduleAuctionSchema
from app.modules.auction.application.usecases.cancel_auction_use_case import CancelAuctionUseCase
from app.modules.auction.application.usecases.create_auction_use_case import CreateAuctionUseCase
from app.modules.auction.application.usecases.finish_auction_use_case import FinishAuctionUseCase
from app.modules.auction.application.usecases.get_auction_by_id_use_case import (
    GetAuctionByIdUseCase,
)
from app.modules.auction.application.usecases.schedule_auction_use_case import (
    ScheduleAuctionUseCase,
)
from app.modules.auction.application.usecases.start_auction_use_case import StartAuctionUseCase
from app.modules.auction.domain.auction_aggregate import Auction
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.exceptions.auction_exceptions import InvalidAuctionIdException
from app.modules.auction.domain.ports.auction_read_repository_interface import (
    IAuctionReadRepository,
)
from app.modules.auction.domain.ports.auction_repository_interface import IAuctionRepository


def _make_auction(status: AuctionStatus, start_time=None, end_time=None) -> Auction:
    return Auction.restore(
        user_id=uuid.uuid4(),
        title="Leilão teste",
        description="Descrição válida",
        start_price=Decimal("100.0"),
        minimum_increment=Decimal("10.0"),
        status=status,
        images=[],
        start_time=start_time,
        end_time=end_time,
    )


class AuctionUseCaseBase:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock(spec=IAuctionRepository)
        self.bus = AsyncMock(spec=EventBusInterface)


class TestCreateAuctionUseCase(AuctionUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.use_case = CreateAuctionUseCase(self.repo, self.bus)

    async def test_saves_and_publishes(self):
        data = CreateAuctionSchema(
            title="Leilão teste",
            description="Descrição",
            start_price=Decimal("100.0"),
            minimum_increment=Decimal("10.0"),
            images=[],
        )

        result = await self.use_case.execute(data, user_id=uuid.uuid4())

        self.repo.save.assert_called_once()
        self.bus.publish.assert_called_once()
        assert result.title == data.title


class TestScheduleAuctionUseCase(AuctionUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.use_case = ScheduleAuctionUseCase(self.repo, self.bus)

    async def test_saves_and_publishes(self):
        auction = _make_auction(status=AuctionStatus.CREATED)
        self.repo.get_by_id.return_value = auction

        data = ScheduleAuctionSchema(
            start_date=datetime.now() + timedelta(hours=1),
            end_date=datetime.now() + timedelta(hours=3),
        )

        await self.use_case.execute(uuid.uuid4(), data)

        self.repo.save.assert_called_once()
        self.bus.publish.assert_called_once()

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        data = ScheduleAuctionSchema(
            start_date=datetime.now() + timedelta(hours=1),
            end_date=datetime.now() + timedelta(hours=3),
        )

        with pytest.raises(InvalidAuctionIdException):
            await self.use_case.execute(uuid.uuid4(), data)


class TestStartAuctionUseCase(AuctionUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.use_case = StartAuctionUseCase(self.repo, self.bus)

    async def test_saves_and_publishes(self):
        now = datetime.now()
        auction = _make_auction(status=AuctionStatus.SCHEDULED, start_time=now)
        self.repo.get_by_id.return_value = auction

        await self.use_case.execute(uuid.uuid4(), current_date=now)

        self.repo.save.assert_called_once()
        self.bus.publish.assert_called_once()

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        with pytest.raises(InvalidAuctionIdException):
            await self.use_case.execute(uuid.uuid4(), current_date=datetime.now())


class TestFinishAuctionUseCase(AuctionUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.use_case = FinishAuctionUseCase(self.repo, self.bus)

    async def test_saves_and_publishes(self):
        now = datetime.now()
        auction = _make_auction(
            status=AuctionStatus.ACTIVE,
            start_time=now - timedelta(hours=2),
            end_time=now,
        )
        self.repo.get_by_id.return_value = auction

        await self.use_case.execute(uuid.uuid4(), current_date=now)

        self.repo.save.assert_called_once()
        self.bus.publish.assert_called_once()

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        with pytest.raises(InvalidAuctionIdException):
            await self.use_case.execute(uuid.uuid4(), current_date=datetime.now())


class TestCancelAuctionUseCase(AuctionUseCaseBase):

    @pytest.fixture(autouse=True)
    def setup(self, setup_mocks):
        self.use_case = CancelAuctionUseCase(self.repo, self.bus)

    async def test_saves_and_publishes(self):
        auction = _make_auction(
            status=AuctionStatus.SCHEDULED,
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
        )
        self.repo.get_by_id.return_value = auction

        await self.use_case.execute(uuid.uuid4(), current_date=datetime.now(), reason="Motivo")

        self.repo.save.assert_called_once()
        self.bus.publish.assert_called_once()

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        with pytest.raises(InvalidAuctionIdException):
            await self.use_case.execute(uuid.uuid4(), current_date=datetime.now())


class TestGetAuctionByIdUseCase:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.repo = AsyncMock(spec=IAuctionReadRepository)
        self.use_case = GetAuctionByIdUseCase(self.repo)

    async def test_returns_auction(self):
        auction = object()
        self.repo.get_by_id.return_value = auction

        result = await self.use_case.execute(str(uuid.uuid4()))

        assert result is auction

    async def test_raises_when_not_found(self):
        self.repo.get_by_id.return_value = None

        with pytest.raises(InvalidAuctionIdException):
            await self.use_case.execute(str(uuid.uuid4()))
