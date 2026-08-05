import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.modules.bidding.infrastructure.persistence.bidding_model import BiddingModel


@pytest.fixture
def bidding_factory(db_session, auction_obj_active):
    async def make_bidding(
        *,
        auction_id: uuid.UUID | None = None,
        current_price: Decimal = Decimal("100.0"),
        minimum_increment: Decimal = Decimal("10.0"),
        last_user_id: uuid.UUID | None = None,
        last_amount: Decimal | None = None,
        timestamp: datetime | None = None,
        count: int = 1,
        **kwargs,
    ):
        biddings = []
        for _ in range(count):
            bidding = BiddingModel(
                auction_id=auction_id or auction_obj_active.id,
                current_price=current_price,
                minimum_increment=minimum_increment,
                last_user_id=last_user_id,
                last_amount=last_amount,
                timestamp=timestamp or datetime.now(UTC),
                **kwargs,
            )
            db_session.add(bidding)
            biddings.append(bidding)
        await db_session.commit()

        return biddings if count > 1 else biddings[0]

    return make_bidding
