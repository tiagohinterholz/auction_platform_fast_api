from typing import Annotated

from fastapi import Depends

from app.core.database.session import SessionDep
from app.core.events.dependencies import EventBusDep
from app.modules.auction.application.usecases.cancel_auction_use_case import (
    CancelAuctionUseCase,
)
from app.modules.auction.application.usecases.create_auction_use_case import (
    CreateAuctionUseCase,
)
from app.modules.auction.application.usecases.get_auction_by_id_use_case import (
    GetAuctionByIdUseCase,
)
from app.modules.auction.application.usecases.schedule_auction_use_case import (
    ScheduleAuctionUseCase,
)
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)
from app.modules.auction.infrastructure.repository.auction_repository import (
    AuctionRepository,
)


def get_auction_repository(session: SessionDep) -> AuctionRepository:
    return AuctionRepository(session)


def get_auction_read_repository(session: SessionDep) -> AuctionReadRepository:
    return AuctionReadRepository(session)


AuctionRepositoryDep = Annotated[AuctionRepository, Depends(get_auction_repository)]
AuctionReadRepositoryDep = Annotated[
    AuctionReadRepository, Depends(get_auction_read_repository)
]


def get_create_auction_use_case(
    repo: AuctionRepositoryDep,
    bus: EventBusDep,
) -> CreateAuctionUseCase:
    return CreateAuctionUseCase(repo, bus)


def get_schedule_auction_use_case(
    repo: AuctionRepositoryDep,
    bus: EventBusDep,
) -> ScheduleAuctionUseCase:
    return ScheduleAuctionUseCase(repo, bus)


def get_cancel_auction_use_case(
    repo: AuctionRepositoryDep,
    bus: EventBusDep,
) -> CancelAuctionUseCase:
    return CancelAuctionUseCase(repo, bus)


def get_auction_by_id_use_case(repo: AuctionReadRepositoryDep) -> GetAuctionByIdUseCase:
    return GetAuctionByIdUseCase(repo)


CreateAuctionUseCaseDep = Annotated[
    CreateAuctionUseCase, Depends(get_create_auction_use_case)
]
ScheduleAuctionUseCaseDep = Annotated[
    ScheduleAuctionUseCase, Depends(get_schedule_auction_use_case)
]
CancelAuctionUseCaseDep = Annotated[
    CancelAuctionUseCase, Depends(get_cancel_auction_use_case)
]
GetAuctionByIdUseCaseDep = Annotated[
    GetAuctionByIdUseCase, Depends(get_auction_by_id_use_case)
]
