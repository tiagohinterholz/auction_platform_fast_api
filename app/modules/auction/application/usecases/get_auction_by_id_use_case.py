from app.modules.auction.domain.exceptions.auction_exceptions import InvalidAuctionIdException
from app.modules.auction.domain.ports.auction_read_repository_interface import (
    IAuctionReadRepository,
)
from app.modules.auction.infrastructure.persistence.auction_read_model import AuctionReadModel


class GetAuctionByIdUseCase:
    def __init__(self, repository: IAuctionReadRepository) -> None:
        self.repository = repository

    async def execute(self, auction_id: str) -> AuctionReadModel:
        auction = await self.repository.get_by_id(auction_id)

        if not auction:
            raise InvalidAuctionIdException(f"Auction with id {auction_id} not found.")

        return auction
