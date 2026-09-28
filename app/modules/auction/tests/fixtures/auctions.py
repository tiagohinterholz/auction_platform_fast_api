from datetime import UTC, datetime, timedelta

import pytest

from app.modules.auction.domain.enums.auction_status import AuctionStatus


@pytest.fixture
async def auction_obj_created(auction_factory, user_obj):
    return await auction_factory(
        status=AuctionStatus.CREATED,
        user_id=user_obj.id,
    )


@pytest.fixture
async def auction_obj_scheduled(auction_factory, user_obj):
    # naive but UTC-equivalent, matching every datetime this app stores -
    # datetime.now() alone is the server's LOCAL time and silently shifted
    # these fixtures by the local UTC offset, causing "active" auctions to
    # actually already be in the past.
    now = datetime.now(UTC).replace(tzinfo=None)
    return await auction_factory(
        status=AuctionStatus.SCHEDULED,
        user_id=user_obj.id,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
    )


@pytest.fixture
async def auction_obj_active(auction_factory, user_obj):
    # naive but UTC-equivalent, matching every datetime this app stores -
    # datetime.now() alone is the server's LOCAL time and silently shifted
    # these fixtures by the local UTC offset, causing "active" auctions to
    # actually already be in the past.
    now = datetime.now(UTC).replace(tzinfo=None)
    return await auction_factory(
        status=AuctionStatus.ACTIVE,
        user_id=user_obj.id,
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=2),
    )


@pytest.fixture
async def auction_obj_finished(auction_factory, user_obj):
    # naive but UTC-equivalent, matching every datetime this app stores -
    # datetime.now() alone is the server's LOCAL time and silently shifted
    # these fixtures by the local UTC offset, causing "active" auctions to
    # actually already be in the past.
    now = datetime.now(UTC).replace(tzinfo=None)
    return await auction_factory(
        status=AuctionStatus.FINISHED,
        user_id=user_obj.id,
        start_time=now - timedelta(hours=3),
        end_time=now - timedelta(hours=1),
    )


@pytest.fixture
async def auction_obj_cancelled(auction_factory, user_obj):
    return await auction_factory(
        status=AuctionStatus.CANCELLED,
        user_id=user_obj.id,
        reason="Cancelled for testing purposes.",
    )
