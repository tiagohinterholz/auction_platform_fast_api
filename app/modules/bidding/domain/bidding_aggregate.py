import uuid
from datetime import datetime

from app.modules.bidding.domain.events.bid_events import BidPlacedEvent
from app.modules.bidding.domain.exceptions.bidding_exceptions import InvalidBidPlaceException


class Bidding:
    def __init__(
        self,
        auction_id: uuid.UUID,
        current_price: float,
        minimum_increment: float, 
        last_user_id: uuid.UUID | None, 
        last_amount: float | None, 
        timestamp: datetime | None = None,
        id: uuid.UUID | None = None, 
    ):
        self._id = id or uuid.uuid4()
        self._current_price = current_price
        self._minimum_increment = minimum_increment
        self._auction_id = auction_id
        self._last_user_id = last_user_id
        self._last_amount = last_amount
        self._timestamp = timestamp or datetime.now()
        self.events: list = []
    
    @classmethod
    def open(cls, auction_id: uuid.UUID, starting_price: float, minimum_increment: float) -> "Bidding":
        return cls(
            auction_id=auction_id,
            current_price=starting_price,
            minimum_increment=minimum_increment,
            last_user_id=None,
            last_amount=None,
        )
    
    @classmethod
    def restore(cls, **kwargs) -> "Bidding":
        bid = cls(**kwargs)
        bid.events = []
        return bid
    
    def place_bid(self, user_id: uuid.UUID, amount: float):
        if amount < self._current_price + self._minimum_increment:
            raise InvalidBidPlaceException(
                f"Bid amount must be at least {self._current_price + self._minimum_increment}"
            )
        
        self._last_user_id = user_id
        self._last_amount = amount
        self._current_price = amount
        self._timestamp = datetime.now()
        self.events.append(
            BidPlacedEvent(
                payload={
                    "auction_id": str(self._auction_id),
                    "user_id": str(user_id),
                    "amount": amount
                }
        ))
    
    def pull_events(self) -> list:
        events = self.events.copy()
        self.events.clear()
        return events
    
    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def current_price(self) -> float:
        return self._current_price

    @property   
    def minimum_increment(self) -> float:
        return self._minimum_increment

    @property
    def auction_id(self) -> uuid.UUID:
        return self._auction_id

    @property
    def last_user_id(self) -> uuid.UUID | None:
        return self._last_user_id

    @property
    def last_amount(self) -> float | None:
        return self._last_amount

    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    