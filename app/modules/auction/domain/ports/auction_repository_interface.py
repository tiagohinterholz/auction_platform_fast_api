from abc import ABC, abstractmethod
from typing import List
from app.modules.auction.domain.auction_aggregate import Auction


class IAuctionRepository(ABC):
    @abstractmethod
    async def create(self, auction: Auction) -> None:
        pass

    @abstractmethod
    async def start(self, auction: Auction) -> None:
        pass

    @abstractmethod
    async def schedule(self, auction: Auction) -> None:
        pass

    @abstractmethod
    async def cancel(self, auction: Auction) -> None:
        pass

    @abstractmethod
    async def finish(self, auction: Auction) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Auction:
        pass

    @abstractmethod
    async def get_all(self) -> List[Auction]:
        pass
