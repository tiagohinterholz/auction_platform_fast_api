from app.core.exceptions.exceptions import DomainException


class InvalidBidPlaceException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)


class AuctionBeingProcessedException(DomainException):
    def __init__(self):
        super().__init__("Auction is currently being processed. Please try again later.")