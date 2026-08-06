from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.bidding.domain.ports.bidding_read_repository_interface import IBidReadRepository
from app.modules.bidding.infrastructure.persistence.bid_read_model import BidReadModel


class BidReadRepository(IBidReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, model: BidReadModel) -> None:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

    async def find_all_by_auction_id(self, auction_id: str) -> Sequence[BidReadModel]:
        result = await self.session.execute(
            select(BidReadModel).where(BidReadModel.auction_id == auction_id)
        )
        return result.scalars().all()
