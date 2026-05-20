import pytest


@pytest.fixture
async def bidding_obj(bidding_factory):
    return await bidding_factory()


@pytest.fixture
async def bidding_obj_with_bid(bidding_factory, user_obj, auction_obj_active):
    return await bidding_factory(
        auction_id=auction_obj_active.id,
        current_price=150.0,
        last_user_id=user_obj.id,
        last_amount=150.0,
    )
