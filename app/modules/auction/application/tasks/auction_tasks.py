import asyncio
import uuid
from datetime import UTC, datetime

from app.core.celery.celery_app import celery_app
from app.core.database.session import AsyncSessionLocal
from app.core.email.dependencies import get_email_service
from app.core.events.in_memory_event_bus import InMemoryEventBus
from app.modules.auction.application.handlers.auction_finished_notification_handler import (
    AuctionFinishedNotificationHandler,
)
from app.modules.auction.application.handlers.finished_auction_handler import AuctionFinishedHandler
from app.modules.auction.application.handlers.started_auction_handler import AuctionStartedHandler
from app.modules.auction.application.usecases.finish_auction_use_case import FinishAuctionUseCase
from app.modules.auction.application.usecases.start_auction_use_case import StartAuctionUseCase
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)
from app.modules.auction.infrastructure.repository.auction_repository import AuctionRepository
from app.modules.bidding.application.handlers.auction_started_handler import (
    AuctionStartedHandler as BiddingAuctionStartedHandler,
)
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.modules.bidding.infrastructure.repository.bidding_repository import BiddingRepository
from app.modules.users.infrastructure.repository.users_repository import UserRepository


async def _start_auction(auction_id: str) -> None:
    async with AsyncSessionLocal() as session:
        write_repo = AuctionRepository(session)
        read_repo = AuctionReadRepository(session)
        bidding_repo = BiddingRepository(session)

        event_bus = InMemoryEventBus()
        event_bus.subscribe("AuctionStartedEvent", AuctionStartedHandler(read_repo).handle)
        event_bus.subscribe("AuctionStartedEvent", BiddingAuctionStartedHandler(bidding_repo).handle)

        use_case = StartAuctionUseCase(write_repo, event_bus)
        await use_case.execute(uuid.UUID(auction_id), datetime.now(UTC))


async def _finish_auction(auction_id: str) -> None:
    async with AsyncSessionLocal() as session:
        write_repo = AuctionRepository(session)
        read_repo = AuctionReadRepository(session)
        bid_read_repo = BidReadRepository(session)
        users_repo = UserRepository(session)

        event_bus = InMemoryEventBus()
        event_bus.subscribe("AuctionFinishedEvent", AuctionFinishedHandler(read_repo).handle)
        event_bus.subscribe(
            "AuctionFinishedEvent",
            AuctionFinishedNotificationHandler(
                bid_read_repository=bid_read_repo,
                users_repository=users_repo,
                email_service=get_email_service(),
            ).handle,
        )

        use_case = FinishAuctionUseCase(write_repo, event_bus)
        await use_case.execute(uuid.UUID(auction_id), datetime.now(UTC))


@celery_app.task(name="start_auction")
def start_auction_task(auction_id: str) -> None:
    asyncio.run(_start_auction(auction_id))


@celery_app.task(name="finish_auction")
def finish_auction_task(auction_id: str) -> None:
    asyncio.run(_finish_auction(auction_id))
