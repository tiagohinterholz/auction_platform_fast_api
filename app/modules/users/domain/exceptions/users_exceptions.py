from app.core.exceptions.exceptions import DomainException


class InvalidUserNameException(DomainException):
    def __init__(self):
        super().__init__("Invalid user name. Name must be a non-empty string.")


class InvalidUserEmailException(DomainException):
    def __init__(self):
        super().__init__("Invalid user email. Email must be a valid email address.")


class InvalidUserCPFException(DomainException):
    def __init__(self):
        super().__init__("Invalid user CPF. CPF must be a non-empty string of 11 characters.")