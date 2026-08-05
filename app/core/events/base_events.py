from abc import ABC
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class BaseDomainEvent(BaseModel, ABC):
    name: str
    payload: dict[str, Any]
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
