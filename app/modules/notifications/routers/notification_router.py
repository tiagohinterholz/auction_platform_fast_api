from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websockets.connection_manager import ConnectionManager
from app.core.events.in_memory_event_bus import InMemoryEventBus
from app.modules.bidding.domain.events.bid_events import BidPlacedEvent
from app.modules.auction.domain.events.auction_events import (
    AuctionStartedEvent,
    AuctionFinishedEvent,
    AuctionCancelledEvent,
    AuctionScheduledEvent,
    AuctionExtendedEvent,
)

router = APIRouter(tags=["Notifications"])


def setup_notifications(manager: ConnectionManager, bus: InMemoryEventBus) -> APIRouter:

    @router.websocket("/ws/auctions/{auction_id}")
    async def websocket_endpoint(websocket: WebSocket, auction_id: str):
        await manager.connect(websocket, auction_id)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket, auction_id)

    async def on_bid_placed(event: BidPlacedEvent) -> None:
        auction_id = str(event.payload["auction_id"])
        await manager.broadcast(auction_id, "bidPlaced", event.payload)

    async def on_auction_started(event: AuctionStartedEvent) -> None:
        auction_id = str(event.payload["id"])
        await manager.broadcast(auction_id, "auctionStarted", event.payload)

    async def on_auction_finished(event: AuctionFinishedEvent) -> None:
        auction_id = str(event.payload["id"])
        await manager.broadcast(auction_id, "auctionFinished", event.payload)

    async def on_auction_cancelled(event: AuctionCancelledEvent) -> None:
        auction_id = str(event.payload["id"])
        await manager.broadcast(auction_id, "auctionCancelled", event.payload)

    async def on_auction_scheduled(event: AuctionScheduledEvent) -> None:
        auction_id = str(event.payload["id"])
        await manager.broadcast(auction_id, "auctionScheduled", event.payload)

    async def on_auction_extended(event: AuctionExtendedEvent) -> None:
        auction_id = str(event.payload["id"])
        await manager.broadcast(auction_id, "auctionExtended", event.payload)

    bus.subscribe("BidPlacedEvent", on_bid_placed)
    bus.subscribe("AuctionStartedEvent", on_auction_started)
    bus.subscribe("AuctionFinishedEvent", on_auction_finished)
    bus.subscribe("AuctionCancelledEvent", on_auction_cancelled)
    bus.subscribe("AuctionScheduledEvent", on_auction_scheduled)
    bus.subscribe("AuctionExtendedEvent", on_auction_extended)

    return router
