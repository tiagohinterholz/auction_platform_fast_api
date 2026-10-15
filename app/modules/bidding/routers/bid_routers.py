from uuid import UUID

from fastapi import APIRouter, status

from app.core.auth.dependencies import CurrentUser
from app.modules.bidding.application.schemas.bid_response_schema import BidResponseSchema
from app.modules.bidding.application.schemas.create_bid_schema import CreateBidSchema
from app.modules.bidding.routers.dependencies import BidReadRepositoryDep, PlaceBidUseCaseDep

router = APIRouter(prefix="/auctions/{auction_id}/bids", tags=["Bidding"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_by_auction_id(
    auction_id: UUID,
    bid_read_repository: BidReadRepositoryDep,
) -> list[BidResponseSchema]:
    bids = await bid_read_repository.find_all_by_auction_id(str(auction_id))
    return [BidResponseSchema.model_validate(bid) for bid in bids]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_bid(
    auction_id: UUID,
    data: CreateBidSchema,
    use_case: PlaceBidUseCaseDep,
    current_user: CurrentUser,
) -> dict:
    await use_case.execute(auction_id, current_user.id, data.amount)
    return {"status": "created"}
