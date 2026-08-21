import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.modules.auction.application.tasks.auction_tasks import _finish_auction, _start_auction
from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.infrastructure.persistence.auction_read_model import AuctionReadModel
from app.modules.bidding.infrastructure.persistence.bid_read_model import BidReadModel
from conftest import TestSessionLocal

# End-to-end tests for the wiring inside auction_tasks.py itself (the exact
# place where two real bugs slipped through before: a dead event
# subscription, and AuctionFinishedEvent never reaching the process that
# had the working handler). These exercise the real event bus + real DB via
# TestSessionLocal, injected through the session_factory parameter, instead
# of mocking each collaborator — the whole point is to catch a wiring
# regression that a pure unit test with mocks wouldn't notice.


class TestFinishAuctionTask:

    async def test_updates_status_to_finished_in_the_read_model(
        self, db_session, auction_factory, user_obj
    ):
        auction = await auction_factory(
            status=AuctionStatus.ACTIVE,
            user_id=user_obj.id,
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() - timedelta(minutes=1),
        )

        await _finish_auction(str(auction.id), session_factory=TestSessionLocal)

        result = await db_session.execute(
            select(AuctionReadModel).where(AuctionReadModel.id == auction.id)
        )
        read_model = result.scalars().first()
        assert read_model.status == AuctionStatus.FINISHED.value

    async def test_notifies_winner_and_loser_without_raising(
        self, db_session, auction_factory, user_obj, user_obj_admin
    ):
        auction = await auction_factory(
            status=AuctionStatus.ACTIVE,
            user_id=user_obj.id,
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() - timedelta(minutes=1),
        )
        db_session.add_all(
            [
                BidReadModel(
                    id=uuid.uuid4(),
                    auction_id=auction.id,
                    user_id=user_obj.id,
                    amount=Decimal("150.00"),
                    timestamp=datetime.now(),
                ),
                BidReadModel(
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
        await _finish_auction(str(auction.id), session_factory=TestSessionLocal)

        result = await db_session.execute(
            select(AuctionReadModel).where(AuctionReadModel.id == auction.id)
        )
        assert result.scalars().first().status == AuctionStatus.FINISHED.value


class TestStartAuctionTask:

    async def test_updates_status_to_active_in_the_read_model(
        self, db_session, auction_factory, user_obj
    ):
        auction = await auction_factory(
            status=AuctionStatus.SCHEDULED,
            user_id=user_obj.id,
            start_time=datetime.now() - timedelta(minutes=1),
            end_time=datetime.now() + timedelta(hours=2),
        )

        await _start_auction(str(auction.id), session_factory=TestSessionLocal)

        result = await db_session.execute(
            select(AuctionReadModel).where(AuctionReadModel.id == auction.id)
        )
        assert result.scalars().first().status == AuctionStatus.ACTIVE.value
