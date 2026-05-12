from app.core.exceptions.exceptions import DomainException


class InvalidBidPlaceException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)