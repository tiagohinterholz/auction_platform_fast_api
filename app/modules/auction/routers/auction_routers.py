from fastapi import APIRouter, Depends, status
from datetime import datetime
from typing import List
import uuid

from app.modules.auction.routers.dependencies import (
    get_auction_repository,
    get_create_auction_use_case,
    get_schedule_auction_use_case,
    get_cancel_auction_use_case,
    get_finish_auction_use_case,
)

from app.modules.auction.infrastructure.repository.auction_repository import (
    AuctionRepository,
)
from app.modules.auction.application.schemas.auction_schema import AuctionSchema


from app.modules.auction.application.schemas.create_auction_schema import (
    CreateAuctionSchema,
)
from app.modules.auction.application.schemas.schedule_auction_schema import (
    ScheduleAuctionSchema,
)
from app.modules.auction.application.schemas.cancel_auction_schema import (
    CancelAuctionSchema,
)

from app.modules.auction.application.usecases.create_auction_use_case import (
    CreateAuctionUseCase,
)
from app.modules.auction.application.usecases.schedule_auction_use_case import (
    ScheduleAuctionUseCase,
)
from app.modules.auction.application.usecases.cancel_auction_use_case import (
    CancelAuctionUseCase,
)
from app.modules.auction.application.usecases.finish_auction_use_case import (
    FinishAuctionUseCase,
)

router = APIRouter(prefix="/auction", tags=["Auction"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_auctions(
    auction_repository: AuctionRepository = Depends(get_auction_repository),
) -> List[AuctionSchema]:
    return await auction_repository.get_all()


@router.get("/{auction_id}", status_code=status.HTTP_200_OK)
async def get_auction_by_id(
    auction_id: uuid.UUID,
    auction_repository: AuctionRepository = Depends(get_auction_repository),
) -> AuctionSchema:
    return await auction_repository.get_by_id(auction_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_auction(
    auction_schema: CreateAuctionSchema,
    usecase: CreateAuctionUseCase = Depends(get_create_auction_use_case),
) -> AuctionSchema:
    return await usecase.execute(auction_schema)


@router.patch("/{auction_id}/schedule", status_code=status.HTTP_200_OK)
async def schedule_auction(
    auction_id: uuid.UUID,
    data: ScheduleAuctionSchema,
    usecase: ScheduleAuctionUseCase = Depends(get_schedule_auction_use_case),
) -> AuctionSchema:
    return await usecase.execute(auction_id, data)


@router.patch("/{auction_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_auction(
    auction_id: uuid.UUID,
    data: CancelAuctionSchema,
    usecase: CancelAuctionUseCase = Depends(get_cancel_auction_use_case),
) -> AuctionSchema:
    return await usecase.execute(
        id=auction_id,
        current_date=datetime.now(),
        reason=data.reason,
    )


@router.patch("/{auction_id}/finish", status_code=status.HTTP_200_OK)
async def finish_auction(
    auction_id: uuid.UUID,
    usecase: FinishAuctionUseCase = Depends(get_finish_auction_use_case),
) -> AuctionSchema:
    return await usecase.execute(auction_id)
