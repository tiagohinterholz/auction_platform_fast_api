from pydantic import BaseModel, EmailStr, Field


class UpdateUserSchema(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
