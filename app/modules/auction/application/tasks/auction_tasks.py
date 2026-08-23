import asyncio
import uuid
from datetime import UTC, datetime

from app.core.celery.celery_app import celery_app
from app.core.config import settings
from app.core.database.session import CelerySessionLocal
from app.core.events.event_bus_interface import EventBusInterface
from app.core.events.in_memory_event_bus import InMemoryEventBus
from app.core.events.rabbitmq_event_bus import RabbitMQEventBus
from app.modules.auction.application.usecases.finish_auction_use_case import FinishAuctionUseCase
from app.modules.auction.application.usecases.start_auction_use_case import StartAuctionUseCase
from app.modules.auction.infrastructure.repository.auction_repository import AuctionRepository


def _make_event_bus() -> EventBusInterface:
    # Deliberately NOT a module-level singleton (unlike main.py's event_bus):
    # each Celery task runs its own asyncio.run(), a brand-new event loop
    # every call, and a RabbitMQEventBus's cached connection is only valid
    # within the loop that opened it. A fresh instance per task, connected
    # and closed within that same task's loop, sidesteps the whole problem.
    return RabbitMQEventBus() if settings.EVENT_BUS_PROVIDER == "rabbitmq" else InMemoryEventBus()


async def _start_auction(
    auction_id: str, session_factory=CelerySessionLocal, bus: EventBusInterface | None = None
) -> None:
    owns_bus = bus is None
    task_bus = bus or _make_event_bus()
    try:
        async with session_factory() as session:
            write_repo = AuctionRepository(session)
            use_case = StartAuctionUseCase(write_repo, task_bus)
            await use_case.execute(uuid.UUID(auction_id), datetime.now(UTC))
    finally:
        if owns_bus and isinstance(task_bus, RabbitMQEventBus):
            await task_bus.close()


async def _finish_auction(
    auction_id: str, session_factory=CelerySessionLocal, bus: EventBusInterface | None = None
) -> None:
    owns_bus = bus is None
    task_bus = bus or _make_event_bus()
    try:
        async with session_factory() as session:
            write_repo = AuctionRepository(session)
            use_case = FinishAuctionUseCase(write_repo, task_bus)
            await use_case.execute(uuid.UUID(auction_id), datetime.now(UTC))
    finally:
        if owns_bus and isinstance(task_bus, RabbitMQEventBus):
            await task_bus.close()


@celery_app.task(name="start_auction")
def start_auction_task(auction_id: str) -> None:
    asyncio.run(_start_auction(auction_id))


@celery_app.task(name="finish_auction")
def finish_auction_task(auction_id: str) -> None:
    asyncio.run(_finish_auction(auction_id))
