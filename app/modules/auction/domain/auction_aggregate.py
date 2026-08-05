import uuid
from datetime import datetime, timedelta

from .enums.auction_status import AuctionStatus
from .events.auction_events import (
    AuctionCancelledEvent,
    AuctionCreatedEvent,
    AuctionExtendedEvent,
    AuctionFinishedEvent,
    AuctionScheduledEvent,
    AuctionStartedEvent,
)
from .exceptions.auction_exceptions import (
    InvalidAuctionDescriptionException,
    InvalidAuctionEndTimeException,
    InvalidAuctionminimumIncrementException,
    InvalidAuctionStartPriceException,
    InvalidAuctionStartTimeException,
    InvalidAuctionStatusException,
    InvalidAuctionTitleException,
)


class Auction:
    def __init__(
        self,
        user_id: uuid.UUID,
        title: str,
        description: str,
        start_price: float,
        minimum_increment: float,
        status: AuctionStatus,
        images: list[str],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        id: uuid.UUID | None = None,
    ):
        self._id = id or uuid.uuid4()
        self._user_id = user_id
        self._title = title
        self._description = description
        self._start_price = start_price
        self._minimum_increment = minimum_increment
        self._start_time = start_time
        self._end_time = end_time
        self._status = status
        self._images = images
        self.events: list = []

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        title: str,
        description: str,
        start_price: float,
        minimum_increment: float,
        status: AuctionStatus,
        images: list[str] | None = None,
    ) -> "Auction":
        if not title.strip():
            raise InvalidAuctionTitleException(title)
        if not description.strip():
            raise InvalidAuctionDescriptionException(description)
        if start_price <= 0:
            raise InvalidAuctionStartPriceException(start_price)
        if minimum_increment <= 0:
            raise InvalidAuctionminimumIncrementException(minimum_increment)
        if status not in AuctionStatus:
            raise InvalidAuctionStatusException(status)

        safe_images = images or []

        auction = cls(
            user_id=user_id,
            title=title,
            description=description,
            start_price=start_price,
            minimum_increment=minimum_increment,
            status=status,
            images=safe_images,
        )
        auction.events.append(
            AuctionCreatedEvent(
                payload={
                    "id": str(auction.id),
                    "user_id": str(auction.user_id),
                    "title": auction.title,
                    "description": auction.description,
                    "start_price": str(auction.start_price),
                    "minimum_increment": str(auction.minimum_increment),
                    "status": auction.status.value,
                    "images": auction.images,
                },
            )
        )
        return auction

    @classmethod
    def restore(cls, **kwargs) -> "Auction":
        auction = cls(**kwargs)
        auction.events = []
        return auction

    def schedule(self, start_time: datetime, end_time: datetime):
        self._assert_transaction(AuctionStatus.CREATED, AuctionStatus.SCHEDULED)

        if start_time >= end_time:
            raise InvalidAuctionStartTimeException(start_time.isoformat())

        if start_time <= datetime.now():
            raise InvalidAuctionStartTimeException(
                f"Scheduling time {start_time} must be after {datetime.now()}."
            )

        self._start_time = start_time
        self._end_time = end_time
        self._status = AuctionStatus.SCHEDULED

        self.events.append(
            AuctionScheduledEvent(
                payload={
                    "id": str(self.id),
                    "start_time": self.start_time.isoformat() if self.start_time else "",
                    "end_time": self.end_time.isoformat() if self.end_time else "",
                    "starting_price": str(self.start_price),
                    "minimum_increment": str(self.minimum_increment),
                }
            )
        )

    def start(self, current_time: datetime):
        self._assert_transaction(AuctionStatus.SCHEDULED, AuctionStatus.ACTIVE)

        if self._start_time is None or self._start_time > current_time:
            raise InvalidAuctionStartTimeException(
                f"Auction cannot be started before {self._start_time}."
            )
        self._start_time = current_time
        self._status = AuctionStatus.ACTIVE

        self.events.append(
            AuctionStartedEvent(
                payload={
                    "id": str(self.id),
                    "start_time": self.start_time.isoformat() if self.start_time else "",
                    "end_time": self.end_time.isoformat() if self.end_time else "",
                    "starting_price": str(self.start_price),
                    "minimum_increment": str(self.minimum_increment),
                    "status": self.status,
                }
            )
        )

    def finish(self, current_time: datetime):
        self._assert_transaction(AuctionStatus.ACTIVE, AuctionStatus.FINISHED)

        if self._end_time is None or self._end_time > current_time:
            raise InvalidAuctionEndTimeException(
                f"Auction cannot be finished before {self._end_time}."
            )
        self._end_time = current_time
        self._status = AuctionStatus.FINISHED

        self.events.append(
            AuctionFinishedEvent(
                payload={
                    "id": str(self.id),
                    "end_time": self.end_time.isoformat() if self.end_time else "",
                }
            )
        )

    def cancel(self, current_time: datetime, reason: str | None = None):
        allowed_status = [AuctionStatus.CREATED, AuctionStatus.SCHEDULED]

        if self._status not in allowed_status:
            raise InvalidAuctionStatusException(
                f"Transition from {self._status} to {AuctionStatus.CANCELLED} is not allowed."
            )

        self._status = AuctionStatus.CANCELLED

        self.events.append(
            AuctionCancelledEvent(
                payload={
                    "id": str(self.id),
                    "cancelled_at": current_time.isoformat(),
                    "reason": reason or "",
                }
            )
        )

    def _assert_transaction(self, from_status: AuctionStatus, to_status: AuctionStatus):
        if self._status != from_status:
            raise InvalidAuctionStatusException(
                f"Transition from {from_status} to {to_status} is not allowed."
            )

    def apply_anti_sniping(self, current_time: datetime):
        if self._status != AuctionStatus.ACTIVE:
            return
        if not self._end_time:
            return

        diff_seconds = (self._end_time - current_time).total_seconds()

        if diff_seconds <= 30:
            self._end_time = current_time + timedelta(seconds=60)
            self.events.append(
                AuctionExtendedEvent(
                    payload={
                        "id": str(self.id),
                        "end_time": self.end_time.isoformat() if self.end_time else "",
                    }
                )
            )

    def pull_events(self) -> list:
        events = self.events.copy()
        self.events.clear()
        return events

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def start_price(self) -> float:
        return self._start_price

    @property
    def minimum_increment(self) -> float:
        return self._minimum_increment

    @property
    def start_time(self) -> datetime | None:
        return self._start_time

    @property
    def end_time(self) -> datetime | None:
        return self._end_time

    @property
    def status(self) -> AuctionStatus:
        return self._status

    @property
    def images(self) -> list[str]:
        return self._images
