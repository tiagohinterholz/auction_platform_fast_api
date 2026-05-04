from app.core.exceptions.exceptions import DomainException
from datetime import datetime


class InvalidAuctionTitleException(DomainException):
    def __init__(self, title: str):
        super().__init__(f"Invalid auction title: {title}")


class InvalidAuctionDescriptionException(DomainException):
    def __init__(self, description: str):
        super().__init__(f"Invalid auction description: {description}")


class InvalidAuctionStartPriceException(DomainException):
    def __init__(self, start_price: float):
        super().__init__(f"Invalid auction start price: {start_price}")


class InvalidAuctionEndTimeException(DomainException):
    def __init__(self, end_time: datetime):
        super().__init__(f"Invalid auction end time: {end_time}")


class InvalidAuctionMinimunIncrementException(DomainException):
    def __init__(self, minimun_increment: float):
        super().__init__(f"Invalid auction minimun increment: {minimun_increment}")


class InvalidAuctionStartTimeException(DomainException):
    def __init__(self, start_time: datetime):
        super().__init__(f"Invalid auction start time: {start_time}")


class InvalidAuctionStatusException(DomainException):
    def __init__(self, status: str):
        super().__init__(f"Invalid auction status: {status}")
