
from abc import ABC, abstractmethod
from typing import Sequence
from app.modules.auction.infrastructure.persistence.auction_read_model import AuctionReadModel

class IAuctionReadRepository(ABC):
    @abstractmethod
    async def save(self, model: AuctionReadModel) -> None:
        pass
    
    @abstractmethod
    async def get_all(self) -> Sequence[AuctionReadModel] | None:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> AuctionReadModel | None:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Sequence[AuctionReadModel] | None:
        pass