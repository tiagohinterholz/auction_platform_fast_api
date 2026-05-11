from passlib.context import CryptContext
from app.modules.auth.domain.ports.password_service_interface import IPasswordService

pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
)

class PasswordService(IPasswordService):

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
            return pwd_context.verify(password, hashed_password)