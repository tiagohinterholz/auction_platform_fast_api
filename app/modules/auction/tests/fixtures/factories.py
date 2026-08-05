import uuid
from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.infrastructure.persistence.auction_model import AuctionModel
from app.modules.auction.infrastructure.persistence.auction_read_model import AuctionReadModel


@pytest.fixture
def auction_factory(db_session, user_obj, faker):
    async def make_auction(
        *,
        title: str | None = None,
        description: str | None = None,
        status: AuctionStatus | None = None,
        user_id: uuid.UUID | None = None,
        start_price: Decimal = Decimal("100.0"),
        minimum_increment: Decimal = Decimal("10.0"),
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        reason: str | None = None,
        images: list | None = None,
        count: int = 1,
        **kwargs,
    ):
        auctions = []
        for _ in range(count):
            _title = title or faker.sentence()
            _description = description or faker.text()
            _status = status.value if status else AuctionStatus.CREATED.value
            _user_id = user_id or user_obj.id

            auction = AuctionModel(
                title=_title,
                description=_description,
                status=_status,
                user_id=_user_id,
                start_price=start_price,
                minimum_increment=minimum_increment,
                start_time=start_time,
                end_time=end_time,
                reason=reason,
                images=images,
                **kwargs,
            )
            db_session.add(auction)
            await db_session.flush()

            read_model = AuctionReadModel(
                id=auction.id,
                title=_title,
                description=_description,
                status=_status,
                user_id=_user_id,
                start_price=start_price,
                minimum_increment=minimum_increment,
                start_time=start_time,
                end_time=end_time,
                reason=reason,
                images=images,
            )
            db_session.add(read_model)
            auctions.append(auction)

        await db_session.commit()

        return auctions if count > 1 else auctions[0]
    return make_auction