import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.core.events.in_memory_event_bus import InMemoryEventBus
from app.modules.auction.application.tasks.auction_tasks import _finish_auction, _start_auction
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.infrastructure.persistence.auction_read_entity import AuctionReadEntity
from app.modules.bidding.infrastructure.persistence.bid_read_entity import BidReadEntity
from conftest import TestSessionLocal
from main import wire_event_handlers

# End-to-end tests for the wiring inside auction_tasks.py itself (the exact
# place where two real bugs slipped through before: a dead event
# subscription, and AuctionFinishedEvent never reaching the process that
# had the working handler). auction_tasks.py only ever *publishes* now — the
# reactions live in main.py's wire_event_handlers, same as production, so
# each test wires its own InMemoryEventBus that way and passes it in via
# `bus=`, instead of mocking each collaborator — the whole point is to catch
# a wiring regression that a pure unit test with mocks wouldn't notice.


@pytest.fixture
async def wired_bus():
    bus = InMemoryEventBus()
    await wire_event_handlers(bus, TestSessionLocal)
    return bus


class TestFinishAuctionTask:

    async def test_updates_status_to_finished_in_the_read_model(
        self, db_session, auction_factory, user_obj, wired_bus
    ):
        auction = await auction_factory(
            status=AuctionStatus.ACTIVE,
            user_id=user_obj.id,
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() - timedelta(minutes=1),
        )

        await _finish_auction(str(auction.id), session_factory=TestSessionLocal, bus=wired_bus)

        result = await db_session.execute(
            select(AuctionReadEntity).where(AuctionReadEntity.id == auction.id)
        )
        read_model = result.scalars().first()
        assert read_model.status == AuctionStatus.FINISHED.value

    async def test_notifies_winner_and_loser_without_raising(
        self, db_session, auction_factory, user_obj, user_obj_admin, wired_bus
    ):
        auction = await auction_factory(
            status=AuctionStatus.ACTIVE,
            user_id=user_obj.id,
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() - timedelta(minutes=1),
        )
        db_session.add_all(
            [
                BidReadEntity(
                    id=uuid.uuid4(),
                    auction_id=auction.id,
                    user_id=user_obj.id,
                    amount=Decimal("150.00"),
                    timestamp=datetime.now(),
                ),
                BidReadEntity(
                    id=uuid.uuid4(),
                    auction_id=auction.id,
                    user_id=user_obj_admin.id,
                    amount=Decimal("100.00"),
                    timestamp=datetime.now(),
                ),
            ]
        )
        await db_session.commit()

        # EMAIL_PROVIDER is forced to "console" for the whole suite (conftest.py),
        # so this exercises the real notification handler without hitting SMTP.
        await _finish_auction(str(auction.id), session_factory=TestSessionLocal, bus=wired_bus)

        result = await db_session.execute(
            select(AuctionReadEntity).where(AuctionReadEntity.id == auction.id)
        )
        assert result.scalars().first().status == AuctionStatus.FINISHED.value


class TestStartAuctionTask:

    async def test_updates_status_to_active_in_the_read_model(
        self, db_session, auction_factory, user_obj, wired_bus
    ):
        auction = await auction_factory(
            status=AuctionStatus.SCHEDULED,
            user_id=user_obj.id,
            start_time=datetime.now() - timedelta(minutes=1),
            end_time=datetime.now() + timedelta(hours=2),
        )

        await _start_auction(str(auction.id), session_factory=TestSessionLocal, bus=wired_bus)

        result = await db_session.execute(
            select(AuctionReadEntity).where(AuctionReadEntity.id == auction.id)
        )
        assert result.scalars().first().status == AuctionStatus.ACTIVE.value
