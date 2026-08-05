import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.auction.domain.auction_aggregate import Auction
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.events.auction_events import (
    AuctionCancelledEvent,
    AuctionCreatedEvent,
    AuctionExtendedEvent,
    AuctionFinishedEvent,
    AuctionScheduledEvent,
    AuctionStartedEvent,
)
from app.modules.auction.domain.exceptions.auction_exceptions import (
    InvalidAuctionDescriptionException,
    InvalidAuctionEndTimeException,
    InvalidAuctionminimumIncrementException,
    InvalidAuctionStartPriceException,
    InvalidAuctionStartTimeException,
    InvalidAuctionStatusException,
    InvalidAuctionTitleException,
)


def _base_create_kwargs(**overrides):
    return {
        "user_id": uuid.uuid4(),
        "title": "Leilão válido",
        "description": "Descrição válida do leilão.",
        "start_price": Decimal("100.0"),
        "minimum_increment": Decimal("10.0"),
        **overrides,
    }


def _make_auction(
    status: AuctionStatus = AuctionStatus.CREATED,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> "Auction":
    return Auction.restore(
        user_id=uuid.uuid4(),
        title="Leilão válido",
        description="Descrição válida do leilão.",
        start_price=Decimal("100.0"),
        minimum_increment=Decimal("10.0"),
        status=status,
        images=[],
        start_time=start_time,
        end_time=end_time,
    )


class TestAuctionAggregate:

    @pytest.mark.parametrize(
        "kwargs, expected_exception",
        [
            (_base_create_kwargs(), None),
            (_base_create_kwargs(title="   "), InvalidAuctionTitleException),
            (_base_create_kwargs(description="   "), InvalidAuctionDescriptionException),
            (_base_create_kwargs(start_price=0), InvalidAuctionStartPriceException),
            (_base_create_kwargs(minimum_increment=0), InvalidAuctionminimumIncrementException),
        ],
        ids=[
            "valid",
            "empty_title",
            "empty_description",
            "zero_price",
            "zero_increment",
        ],
    )
    def test_auction_create(self, kwargs, expected_exception):
        if expected_exception:
            with pytest.raises(expected_exception):
                Auction.create(**kwargs)
        else:
            auction = Auction.create(**kwargs)
            assert auction.title == kwargs["title"]
            assert auction.status == AuctionStatus.CREATED
            assert len(auction.events) == 1
            assert isinstance(auction.events[0], AuctionCreatedEvent)
    
    @pytest.mark.parametrize(
        "status, start_time, end_time, expected_exception",
        [
            (AuctionStatus.CREATED, datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=3), None),
            (AuctionStatus.ACTIVE,  datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=3), InvalidAuctionStatusException),
            (AuctionStatus.CREATED, datetime.now() + timedelta(hours=3), datetime.now() + timedelta(hours=1), InvalidAuctionStartTimeException),
            (AuctionStatus.CREATED, datetime.now() - timedelta(hours=1), datetime.now() + timedelta(hours=3), InvalidAuctionStartTimeException),
        ],
        ids=["valid", "wrong_status", "start_after_end", "start_in_past"],
    )
    def test_auction_schedule(self, status, start_time, end_time, expected_exception):
        auction = _make_auction(status=status)
        if expected_exception:
            with pytest.raises(expected_exception):
                auction.schedule(start_time, end_time)
        else:
            auction.schedule(start_time, end_time)
            assert auction.status == AuctionStatus.SCHEDULED
            assert auction.start_time == start_time
            assert auction.end_time == end_time
            assert any(isinstance(event, AuctionScheduledEvent) for event in auction.events)
    
    
    @pytest.mark.parametrize(
        "status, start_time, current_time, expected_exception",
        [
            (AuctionStatus.SCHEDULED, datetime.now(), datetime.now(), None),
            (AuctionStatus.ACTIVE,  datetime.now() + timedelta(hours=1), datetime.now(), InvalidAuctionStatusException),
            (AuctionStatus.SCHEDULED, datetime.now() + timedelta(hours=1), datetime.now(), InvalidAuctionStartTimeException),
        ],
        ids=["valid", "wrong_status", "start_early"],
    )
    def test_auction_start(self, status, start_time, current_time, expected_exception):
        auction = _make_auction(status=status, start_time=start_time)
        if expected_exception:
            with pytest.raises(expected_exception):
                auction.start(current_time=current_time)
        else:
            auction.start(current_time=current_time)
            assert auction.status == AuctionStatus.ACTIVE
            assert any(isinstance(event, AuctionStartedEvent) for event in auction.events)
    
    @pytest.mark.parametrize(
        "status, reason, expected_exception",
        [
            (AuctionStatus.SCHEDULED, "Motivo válido", None),
            (AuctionStatus.ACTIVE,  "Motivo válido", InvalidAuctionStatusException),
        ],
        ids=["valid", "wrong_status"],
    )
    def test_auction_cancel(self, status, reason, expected_exception):
        auction = _make_auction(status=status, start_time=datetime.now() + timedelta(hours=1), end_time=datetime.now() + timedelta(hours=2))
        if expected_exception:
            with pytest.raises(expected_exception):
                auction.cancel(current_time=datetime.now(), reason=reason)
        else:
            auction.cancel(current_time=datetime.now(), reason=reason)
            assert auction.status == AuctionStatus.CANCELLED
            assert any(isinstance(event, AuctionCancelledEvent) for event in auction.events)
    
    @pytest.mark.parametrize(
        "status, end_time, current_time, expected_exception",
        [
            (AuctionStatus.ACTIVE, datetime.now(), datetime.now(), None),
            (AuctionStatus.SCHEDULED,  datetime.now() + timedelta(hours=1), datetime.now(), InvalidAuctionStatusException),
            (AuctionStatus.ACTIVE, datetime.now() + timedelta(hours=1), datetime.now(), InvalidAuctionEndTimeException),
        ],
        ids=["valid", "wrong_status", "finish_early"],
    )
    def test_auction_finish(self, status, end_time, current_time, expected_exception):
        auction = _make_auction(status=status, start_time=datetime.now() - timedelta(hours=2), end_time=end_time)
        if expected_exception:
            with pytest.raises(expected_exception):
                auction.finish(current_time=current_time)
        else:
            auction.finish(current_time=current_time)
            assert auction.status == AuctionStatus.FINISHED
            assert any(isinstance(event, AuctionFinishedEvent) for event in auction.events)
    
    def test_anti_sniping_extends_when_bid_near_end(self):
        now = datetime.now()
        auction = _make_auction(
            status=AuctionStatus.ACTIVE,
            end_time=now + timedelta(seconds=20),
        )
        auction.apply_anti_sniping(current_time=now)

        assert auction.end_time == now + timedelta(seconds=60)
        assert any(isinstance(e, AuctionExtendedEvent) for e in auction.events)

    def test_anti_sniping_does_nothing_when_time_is_safe(self):
        now = datetime.now()
        original_end = now + timedelta(minutes=5)
        auction = _make_auction(status=AuctionStatus.ACTIVE, end_time=original_end)

        auction.apply_anti_sniping(current_time=now)

        assert auction.end_time == original_end  # não mudou
        assert not any(isinstance(e, AuctionExtendedEvent) for e in auction.events)

    def test_anti_sniping_does_nothing_when_not_active(self):
        now = datetime.now()
        auction = _make_auction(
            status=AuctionStatus.CREATED,
            end_time=now + timedelta(seconds=10),
        )
        auction.apply_anti_sniping(current_time=now)

        assert not any(isinstance(e, AuctionExtendedEvent) for e in auction.events)