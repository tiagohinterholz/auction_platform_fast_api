from abc import ABC, abstractmethod

from app.modules.bidding.domain.bidding_aggregate import Bidding


class IBiddingRepository(ABC):
    @abstractmethod
    async def find_by_auction_id(self, auction_id: str) -> Bidding:
        pass
    
    @abstractmethod
    async def save(self, bidding: Bidding) -> None:
        pass