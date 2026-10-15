
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.core.auth.dependencies import CurrentUser
from app.modules.auction.application.schemas.auction_schema import AuctionSchema
from app.modules.auction.application.schemas.cancel_auction_schema import CancelAuctionSchema
from app.modules.auction.application.schemas.create_auction_schema import CreateAuctionSchema
from app.modules.auction.application.schemas.schedule_auction_schema import ScheduleAuctionSchema
from app.modules.auction.routers.dependencies import (
    AuctionReadRepositoryDep,
    CancelAuctionUseCaseDep,
    CreateAuctionUseCaseDep,
    GetAuctionByIdUseCaseDep,
    ScheduleAuctionUseCaseDep,
)

router = APIRouter(prefix="/auctions", tags=["Auction"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_auctions(
    auction_repository: AuctionReadRepositoryDep,
) -> list[AuctionSchema]:
    auctions = await auction_repository.get_all()
    return [AuctionSchema.model_validate(auction) for auction in auctions]

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_auctions(
    auction_repository: AuctionReadRepositoryDep,
    current_user: CurrentUser,
) -> list[AuctionSchema]:
    auctions = await auction_repository.get_by_user_id(str(current_user.id))
    return [AuctionSchema.model_validate(auction) for auction in auctions]

@router.get("/{auction_id}", status_code=status.HTTP_200_OK)
async def get_auction_by_id(
    auction_id: uuid.UUID,
    usecase: GetAuctionByIdUseCaseDep,
) -> AuctionSchema:
    auction = await usecase.execute(str(auction_id))
    return AuctionSchema.model_validate(auction)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_auction(
    data: CreateAuctionSchema,
    usecase: CreateAuctionUseCaseDep,
    current_user: CurrentUser,
) -> AuctionSchema:
    auction = await usecase.execute(data, user_id=current_user.id)
    return AuctionSchema.model_validate(auction)


@router.patch("/{auction_id}/schedule", status_code=status.HTTP_202_ACCEPTED)
async def schedule_auction(
    auction_id: uuid.UUID,
    data: ScheduleAuctionSchema,
    usecase: ScheduleAuctionUseCaseDep,
    _: CurrentUser,
) -> AuctionSchema:
    auction = await usecase.execute(auction_id, data)
    return AuctionSchema.model_validate(auction)


@router.patch("/{auction_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
async def cancel_auction(
    auction_id: uuid.UUID,
    data: CancelAuctionSchema,
    usecase: CancelAuctionUseCaseDep,
    _: CurrentUser,
) -> AuctionSchema:
    auction = await usecase.execute(
        id=auction_id,
        current_date=datetime.now(UTC),
        reason=data.reason,
    )
    return AuctionSchema.model_validate(auction)
