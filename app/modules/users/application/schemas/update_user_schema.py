from pydantic import BaseModel, EmailStr, Field


class CreateUserSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    cpf: str = Field(..., min_length=11, max_length=11)
    password: str = Field(..., min_length=6)


class UpdateUserSchema(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
