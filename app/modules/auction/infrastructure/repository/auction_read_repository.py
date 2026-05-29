from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Sequence
from app.modules.auction.infrastructure.persistence.auction_read_model import (
    AuctionReadModel,
)
from app.modules.auction.domain.ports.auction_read_repository_interface import IAuctionReadRepository


class AuctionReadRepository(IAuctionReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, model: AuctionReadModel) -> None:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

    async def get_by_id(self, id: str) -> AuctionReadModel | None:
        query = select(AuctionReadModel).where(AuctionReadModel.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self) -> Sequence[AuctionReadModel]:
        query = select(AuctionReadModel)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_user_id(self, user_id: str) -> Sequence[AuctionReadModel]:
        query = select(AuctionReadModel).where(AuctionReadModel.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()