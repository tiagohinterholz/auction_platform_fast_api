import uuid

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str