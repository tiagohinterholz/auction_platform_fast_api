from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.bidding.domain.bidding_aggregate import Bidding
from app.modules.bidding.domain.ports.bidding_repository_interface import IBiddingRepository
from app.modules.bidding.infrastructure.persistence.bidding_model import BiddingModel


class BiddingRepository(IBiddingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, model: BiddingModel) -> Bidding:
        return Bidding.restore(
            id=model.id,
            auction_id=model.auction_id,
            current_price=model.current_price,
            minimum_increment=model.minimum_increment,
            last_user_id=model.last_user_id,
            last_amount=model.last_amount,
            timestamp=model.timestamp,
        )

    async def find_by_auction_id(self, auction_id: str) -> Bidding | None:
        result = await self.session.execute(
            select(BiddingModel).where(BiddingModel.auction_id == auction_id)
        )
        model = result.scalars().first()
        if not model:
            return None
        return self._to_domain(model)

    async def save(self, bidding: Bidding) -> None:
        model = BiddingModel(
            id=bidding.id,
            auction_id=bidding.auction_id,
            current_price=bidding.current_price,
            minimum_increment=bidding.minimum_increment,
            last_user_id=bidding.last_user_id,
            last_amount=bidding.last_amount,
            timestamp=bidding.timestamp,
        )
        await self.session.merge(model)
        await self.session.commit()
