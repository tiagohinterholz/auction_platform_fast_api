import uuid
from decimal import Decimal

import pytest

from app.modules.bidding.domain.bidding_aggregate import Bidding
from app.modules.bidding.domain.exceptions.bidding_exceptions import InvalidBidPlaceException


class TestBiddingAggregate:

    def test_place_bid_updates_current_price(self):
        bidding = Bidding.open(
            auction_id=uuid.uuid4(), starting_price=Decimal("100.0"), minimum_increment=Decimal("10.0")
        )

        bidding.place_bid(user_id=uuid.uuid4(), amount=Decimal("120.0"))

        assert bidding.current_price == Decimal("120.0")


    def test_place_bid_below_minimum_raises(self):
        bidding = Bidding.open(
            auction_id=uuid.uuid4(), starting_price=Decimal("100.0"), minimum_increment=Decimal("10.0")
        )

        with pytest.raises(InvalidBidPlaceException):
            bidding.place_bid(user_id=uuid.uuid4(), amount=Decimal("105.0"))  # mínimo seria 110
