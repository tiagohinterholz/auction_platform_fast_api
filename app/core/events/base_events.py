from abc import ABC
from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field


class BaseDomainEvent(BaseModel, ABC):
    name: str
    payload: Dict[str, Any]
    occured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
