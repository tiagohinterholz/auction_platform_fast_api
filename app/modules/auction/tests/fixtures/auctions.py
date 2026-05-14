from datetime import datetime, timedelta, timezone

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
    now = datetime.now(timezone.utc)
    return await auction_factory(
        status=AuctionStatus.SCHEDULED,
        user_id=user_obj.id,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
    )


@pytest.fixture
async def auction_obj_active(auction_factory, user_obj):
    now = datetime.now(timezone.utc)
    return await auction_factory(
        status=AuctionStatus.ACTIVE,
        user_id=user_obj.id,
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=2),
    )


@pytest.fixture
async def auction_obj_finished(auction_factory, user_obj):
    now = datetime.now(timezone.utc)
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
