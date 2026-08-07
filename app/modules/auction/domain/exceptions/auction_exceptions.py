from decimal import Decimal

from app.core.exceptions.exceptions import ConflictException, DomainException, NotFoundException


class InvalidAuctionTitleException(DomainException):
    def __init__(self, title: str):
        super().__init__(f"Invalid auction title: {title}")


class InvalidAuctionIdException(NotFoundException):
    def __init__(self, id: str):
        super().__init__(f"Invalid auction id: {id}")


class InvalidAuctionDescriptionException(DomainException):
    def __init__(self, description: str):
        super().__init__(f"Invalid auction description: {description}")


class InvalidAuctionStartPriceException(DomainException):
    def __init__(self, start_price: Decimal):
        super().__init__(f"Invalid auction start price: {start_price}")


class InvalidAuctionEndTimeException(DomainException):
    def __init__(self, end_time: str):
        super().__init__(f"Invalid auction end time: {end_time}")


class InvalidAuctionminimumIncrementException(DomainException):
    def __init__(self, minimum_increment: Decimal):
        super().__init__(f"Invalid auction minimum increment: {minimum_increment}")


class InvalidAuctionStartTimeException(DomainException):
    def __init__(self, start_time: str):
        super().__init__(f"Invalid auction start time: {start_time}")


class InvalidAuctionStatusException(ConflictException):
    def __init__(self, status: str):
        super().__init__(f"Invalid auction status: {status}")


class AuctionNotFoundException(NotFoundException):
    def __init__(self, auction_id: str):
        super().__init__(f"Auction with id {auction_id} not found.")
