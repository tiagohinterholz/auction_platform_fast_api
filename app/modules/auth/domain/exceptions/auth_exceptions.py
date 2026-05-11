from app.core.exceptions.exceptions import DomainException


class InvalidCredentialsException(DomainException):
    def __init__(self):
        super().__init__("Invalid credentials")


class TokenExpiredException(DomainException):
    def __init__(self):
        super().__init__("Token expired.")


class TokenRevokedException(DomainException):
    def __init__(self):
        super().__init__("Token revoked.")