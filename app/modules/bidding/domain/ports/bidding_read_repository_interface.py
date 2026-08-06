
from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.modules.bidding.infrastructure.persistence.bid_read_model import BidReadModel


class IBidReadRepository(ABC):
    @abstractmethod
    async def save(self, model: BidReadModel) -> None:
        pass

    @abstractmethod
    async def find_all_by_auction_id(self, auction_id: str) -> Sequence[BidReadModel] | None:
        pass