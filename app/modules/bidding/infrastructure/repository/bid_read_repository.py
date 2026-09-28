from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.bidding.domain.ports.bidding_read_repository_interface import IBidReadRepository
from app.modules.bidding.domain.read_models.bid_read_model import BidReadModel
from app.modules.bidding.infrastructure.persistence.bid_read_entity import BidReadEntity


class BidReadRepository(IBidReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    def _to_domain(self, model: BidReadEntity) -> BidReadModel:
        return BidReadModel(
            id=model.id,
            auction_id=model.auction_id,
            user_id=model.user_id,
            amount=model.amount,
            timestamp=model.timestamp,
        )

    async def save(self, model: BidReadModel) -> None:
        read_entity = BidReadEntity(
            id=model.id,
            auction_id=model.auction_id,
            user_id=model.user_id,
            amount=model.amount,
            timestamp=model.timestamp,
        )
        await self.session.merge(read_entity)
        await self.session.commit()

    async def find_all_by_auction_id(self, auction_id: str) -> Sequence[BidReadModel]:
        result = await self.session.execute(
            select(BidReadEntity)
            .where(BidReadEntity.auction_id == auction_id)
            .order_by(BidReadEntity.timestamp.desc())
        )
        bid_entities = result.scalars().all()

        return [self._to_domain(model) for model in bid_entities]