from app.core.exceptions.exceptions import UnauthorizedException


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid credentials")


class EmailAlreadyRegisteredException(UnauthorizedException):
    def __init__(self):
        super().__init__("Email already registered")


class TokenExpiredException(UnauthorizedException):
    def __init__(self):
        super().__init__("Token expired.")


class TokenRevokedException(UnauthorizedException):
    def __init__(self):
        super().__init__("Token revoked.")
