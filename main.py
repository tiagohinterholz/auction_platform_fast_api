from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database.session import AsyncSessionLocal
from app.core.events.in_memory_event_bus import InMemoryEventBus
from app.core.exceptions.error_handlers import setup_exception_handlers
from app.core.redis.client import create_redis_client
from app.core.websockets.connection_manager import ConnectionManager
from app.modules.auction.application.handlers.bid_placed_handler import (
    BidPlacedHandler as AuctionBidPlacedHandler,
)
from app.modules.auction.application.handlers.cancelled_auction_handler import (
    AuctionCancelledHandler,
)
from app.modules.auction.application.handlers.created_auction_handler import AuctionCreatedHandler
from app.modules.auction.application.handlers.finished_auction_handler import AuctionFinishedHandler
from app.modules.auction.application.handlers.scheduled_auction_handler import (
    AuctionScheduledHandler,
)
from app.modules.auction.application.handlers.started_auction_handler import AuctionStartedHandler
from app.modules.auction.infrastructure.repository.auction_read_repository import (
    AuctionReadRepository,
)
from app.modules.auction.infrastructure.repository.auction_repository import AuctionRepository
from app.modules.auction.routers.auction_routers import router as auction_router
from app.modules.auth.routers.auth_router import router as auth_router
from app.modules.bidding.application.handlers.bid_placed_handler import (
    BidPlacedHandler as BiddingBidPlacedHandler,
)
from app.modules.bidding.infrastructure.repository.bid_read_repository import BidReadRepository
from app.modules.bidding.routers.bid_routers import router as bidding_router
from app.modules.notifications.routers.notification_router import setup_notifications
from app.modules.users.routers.users_router import router as users_router

event_bus = InMemoryEventBus()
connection_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = create_redis_client()
    app.state.event_bus = event_bus
    app.state.connection_manager = connection_manager

    async def on_auction_created(e):
        async with AsyncSessionLocal() as session:
            await AuctionCreatedHandler(AuctionReadRepository(session)).handle(e)

    async def on_auction_scheduled(e):
        async with AsyncSessionLocal() as session:
            await AuctionScheduledHandler(AuctionReadRepository(session)).handle(e)

    async def on_auction_started(e):
        async with AsyncSessionLocal() as session:
            await AuctionStartedHandler(AuctionReadRepository(session)).handle(e)

    async def on_auction_finished(e):
        async with AsyncSessionLocal() as session:
            await AuctionFinishedHandler(AuctionReadRepository(session)).handle(e)

    async def on_auction_cancelled(e):
        async with AsyncSessionLocal() as session:
            await AuctionCancelledHandler(AuctionReadRepository(session)).handle(e)

    async def on_bid_placed_auction(e):
        async with AsyncSessionLocal() as session:
            await AuctionBidPlacedHandler(
                write_repository=AuctionRepository(session),
                read_repository=AuctionReadRepository(session),
                event_bus=event_bus,
            ).handle(e)

    async def on_bid_placed_bidding(e):
        async with AsyncSessionLocal() as session:
            await BiddingBidPlacedHandler(BidReadRepository(session)).handle(e)

    event_bus.subscribe("AuctionCreatedEvent", on_auction_created)
    event_bus.subscribe("AuctionScheduledEvent", on_auction_scheduled)
    event_bus.subscribe("AuctionStartedEvent", on_auction_started)
    event_bus.subscribe("AuctionFinishedEvent", on_auction_finished)
    event_bus.subscribe("AuctionCancelledEvent", on_auction_cancelled)
    event_bus.subscribe("BidPlacedEvent", on_bid_placed_auction)
    event_bus.subscribe("BidPlacedEvent", on_bid_placed_bidding)

    yield

    await app.state.redis.aclose()


app = FastAPI(
    title="Auction Platform API",
    description="API for managing auctions, bids, and users in an auction platform.",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(auction_router, prefix="/api/v1")
app.include_router(bidding_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(
    setup_notifications(manager=connection_manager, bus=event_bus),
    prefix="/api/v1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)


@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok"})
