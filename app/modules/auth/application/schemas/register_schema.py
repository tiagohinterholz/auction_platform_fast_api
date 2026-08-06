import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    cpf: str = Field(..., min_length=11, max_length=11)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")
        return value
