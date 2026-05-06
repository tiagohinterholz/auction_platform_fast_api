from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.auction.domain.auction_aggregate import Auction
from app.modules.auction.domain.ports.auction_repository_interface import IAuctionRepository
from app.modules.auction.infrastructure.persistence.auction_model import AuctionModel


class AuctionRepository(IAuctionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_domain(self, model: AuctionModel) -> Auction:
        return Auction.restore(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            description=model.description,
            start_price=model.start_price,
            minimun_increment=model.minimun_increment,
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
            images=model.images or [],
        )

    async def get_by_id(self, id: str) -> Auction | None:
        result = await self.session.execute(
            select(AuctionModel).where(AuctionModel.id == id)
        )
        auction_model = result.scalars().first()
        if not auction_model:
            return None
        return self._to_domain(auction_model)
    
    async def save(self, auction: Auction) -> None:
        auction_model = AuctionModel(
            id=auction.id,
            user_id=auction.user_id,
            title=auction.title,
            description=auction.description,
            start_price=auction.start_price,
            minimun_increment=auction.minimun_increment,
            start_time=auction.start_time,
            end_time=auction.end_time,
            status=auction.status,
            images=auction.images,
        )
        await self.session.merge(auction_model)
        await self.session.commit()
    
    async def get_all(self) -> list[Auction]:
        result = await self.session.execute(select(AuctionModel))
        auction_models = result.scalars().all()
        return [self._to_domain(model) for model in auction_models]