
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status

from app.core.auth.dependencies import get_current_user
from app.modules.auction.application.schemas.auction_schema import AuctionSchema
from app.modules.auction.application.schemas.cancel_auction_schema import CancelAuctionSchema
from app.modules.auction.application.schemas.create_auction_schema import CreateAuctionSchema
from app.modules.auction.application.schemas.schedule_auction_schema import ScheduleAuctionSchema
from app.modules.auction.application.usecases.cancel_auction_use_case import CancelAuctionUseCase
from app.modules.auction.application.usecases.create_auction_use_case import CreateAuctionUseCase
from app.modules.auction.application.usecases.schedule_auction_use_case import (
    ScheduleAuctionUseCase,
)
from app.modules.auction.domain.exceptions.auction_exceptions import InvalidAuctionIdException
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)
from app.modules.auction.routers.dependencies import (
    get_auction_read_repository,
    get_cancel_auction_use_case,
    get_create_auction_use_case,
    get_schedule_auction_use_case,
)
from app.modules.users.domain.users_aggregate import User

router = APIRouter(prefix="/auctions", tags=["Auction"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_auctions(
    auction_repository: AuctionReadRepository = Depends(get_auction_read_repository),
) -> list[AuctionSchema]:
    auctions = await auction_repository.get_all()
    return [AuctionSchema.model_validate(auction) for auction in auctions]

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_auctions(
    auction_repository: AuctionReadRepository = Depends(get_auction_read_repository),
    current_user: User = Depends(get_current_user),
) -> list[AuctionSchema]:
    auctions = await auction_repository.get_by_user_id(str(current_user.id))
    return [AuctionSchema.model_validate(auction) for auction in auctions]

@router.get("/{auction_id}", status_code=status.HTTP_200_OK)
async def get_auction_by_id(
    auction_id: uuid.UUID,
    auction_repository: AuctionReadRepository = Depends(get_auction_read_repository),
) -> AuctionSchema:
    auction = await auction_repository.get_by_id(str(auction_id))
    if not auction:
        raise InvalidAuctionIdException(f"Auction with id {auction_id} not found.")
    
    return AuctionSchema.model_validate(auction)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_auction(
    data: CreateAuctionSchema,
    usecase: CreateAuctionUseCase = Depends(get_create_auction_use_case),
    current_user: User = Depends(get_current_user),
) -> AuctionSchema:
    auction = await usecase.execute(data, user_id=current_user.id)
    return AuctionSchema.model_validate(auction)


@router.patch("/{auction_id}/schedule", status_code=status.HTTP_202_ACCEPTED)
async def schedule_auction(
    auction_id: uuid.UUID,
    data: ScheduleAuctionSchema,
    usecase: ScheduleAuctionUseCase = Depends(get_schedule_auction_use_case),
    _: User = Depends(get_current_user),
) -> AuctionSchema:
    auction = await usecase.execute(auction_id, data)
    return AuctionSchema.model_validate(auction)


@router.patch("/{auction_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
async def cancel_auction(
    auction_id: uuid.UUID,
    data: CancelAuctionSchema,
    usecase: CancelAuctionUseCase = Depends(get_cancel_auction_use_case),
    _: User = Depends(get_current_user),
) -> AuctionSchema:
    auction = await usecase.execute(
        id=auction_id,
        current_date=datetime.now(),
        reason=data.reason,
    )
    return AuctionSchema.model_validate(auction)
