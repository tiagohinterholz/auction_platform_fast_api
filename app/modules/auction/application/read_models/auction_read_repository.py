from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.modules.auction.application.read_models.auction_read_model import (
    AuctionReadModel,
)


class AuctionReadRepository:
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

    async def get_all(self) -> List[AuctionReadModel]:
        query = select(AuctionReadModel)
        result = await self.session.execute(query)
        return result.scalars().all()
