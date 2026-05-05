from abc import ABC, abstractmethod
from typing import List
from app.modules.auction.domain.auction_aggregate import Auction


class IAuctionRepository(ABC):
    @abstractmethod
    async def save(self, auction: Auction) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Auction:
        pass

