class DomainException(Exception):
    status_code: int = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundException(DomainException):
    """Resource referenced by the request doesn't exist. Maps to HTTP 404."""

    status_code = 404


class UnauthorizedException(DomainException):
    """Credentials/token missing, invalid or expired. Maps to HTTP 401."""

    status_code = 401


class ConflictException(DomainException):
    """Request conflicts with the resource's current state. Maps to HTTP 409."""

    status_code = 409
