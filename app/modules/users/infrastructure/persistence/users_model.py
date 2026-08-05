import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="USER")
    is_active = Column(Boolean, nullable=False, default=True)
