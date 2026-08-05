from enum import Enum


class AuctionStatus(str, Enum):
    CREATED = "created"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"
