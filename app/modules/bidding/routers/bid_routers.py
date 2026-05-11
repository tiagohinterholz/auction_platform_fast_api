from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status

from app.modules.bidding.application.schemas.create_bid_schema import CreateBidSchema
from app.modules.bidding.application.schemas.bid_response_schema import BidResponseSchema
from app.modules.bidding.application.usecases.place_bid_use_case import PlaceBidUseCase
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.modules.bidding.routers.dependencies import get_place_bid_use_case, get_bid_read_repository
from app.core.auth.dependencies import get_current_user
from app.modules.users.domain.users_aggregate import User

router = APIRouter(prefix="/auctions/{auction_id}/bids", tags=["Bidding"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_by_auction_id(
    auction_id: UUID,
    bid_read_repository: BidReadRepository = Depends(get_bid_read_repository),
) -> List[BidResponseSchema]:
    bids = await bid_read_repository.find_all_by_auction_id(str(auction_id))
    return [BidResponseSchema.model_validate(bid) for bid in bids]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_bid(
    auction_id: UUID,
    data: CreateBidSchema,
    use_case: PlaceBidUseCase = Depends(get_place_bid_use_case),
    current_user: User = Depends(get_current_user),
) -> dict:
    await use_case.execute(auction_id, current_user.id, data.amount)
    return {"status": "created"}
