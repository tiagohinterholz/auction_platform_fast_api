import uuid
from datetime import datetime

import pytest

from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.infrastructure.persistence.auction_model import AuctionModel


@pytest.fixture
def auction_factory(db_session, user_obj, faker):
    async def make_auction(
        *,
        title: str | None = None,
        description: str | None = None,
        status: AuctionStatus | None = None,
        user_id: uuid.UUID | None = None,
        start_price: float = 100.0,
        minimum_increment: float = 10.0,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        reason: str | None = None,
        images: list | None = None,
        count: int = 1,
        **kwargs,
    ):
        auctions = []
        for _ in range(count):
            auction = AuctionModel(
                title=title or faker.sentence(),
                description=description or faker.text(),
                status=status.value if status else AuctionStatus.CREATED.value,
                user_id=user_id or user_obj.id,
                start_price=start_price,
                minimum_increment=minimum_increment,
                start_time=start_time,
                end_time=end_time,
                reason=reason,
                images=images,
                **kwargs,
            )
            db_session.add(auction)
            auctions.append(auction)
        await db_session.commit()

        return auctions if count > 1 else auctions[0]   
    return make_auction