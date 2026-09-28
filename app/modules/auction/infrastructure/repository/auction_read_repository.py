from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.auction.domain.enums.auction_status import AuctionStatus
from app.modules.auction.domain.ports.auction_read_repository_interface import (
    IAuctionReadRepository,
)
from app.modules.auction.domain.read_models.auction_read_model import AuctionReadModel
from app.modules.auction.infrastructure.persistence.auction_read_entity import (
    AuctionReadEntity,
)


class AuctionReadRepository(IAuctionReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    def _to_domain(self, model: AuctionReadEntity) -> AuctionReadModel:
        return AuctionReadModel(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            description=model.description,
            start_price=model.start_price,
            minimum_increment=model.minimum_increment,
            start_time=model.start_time,
            highest_bid=model.highest_bid,
            end_time=model.end_time,
            status=AuctionStatus(model.status),
            reason=model.reason,
            images=model.images or [],
            )

    async def save(self, model: AuctionReadModel) -> None:
        auction_read_entity = AuctionReadEntity(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            description=model.description,
            start_price=model.start_price,
            minimum_increment=model.minimum_increment,
            start_time=model.start_time,
            end_time=model.end_time,
            highest_bid=model.highest_bid,
            status=model.status,
            images=model.images,
        )
        await self.session.merge(auction_read_entity)
        await self.session.commit()

    async def get_by_id(self, id: str) -> AuctionReadModel | None:
        query = select(AuctionReadEntity).where(AuctionReadEntity.id == id)
        result = await self.session.execute(query)
        auction_entity = result.scalars().first()
        if not auction_entity:
            return None
        return self._to_domain(auction_entity)

    async def get_all(self) -> Sequence[AuctionReadModel]:
        query = select(AuctionReadEntity)
        result = await self.session.execute(query)
        auction_entities = result.scalars().all()
        return [self._to_domain(model) for model in auction_entities]

    async def get_by_user_id(self, user_id: str) -> Sequence[AuctionReadModel]:
        query = select(AuctionReadEntity).where(AuctionReadEntity.user_id == user_id)
        result = await self.session.execute(query)
        auction_entities = result.scalars().all()
        return [self._to_domain(model) for model in auction_entities]