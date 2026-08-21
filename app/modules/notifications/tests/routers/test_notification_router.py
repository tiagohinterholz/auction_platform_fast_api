from unittest.mock import AsyncMock

from app.core.events.in_memory_event_bus import InMemoryEventBus
from app.core.websockets.connection_manager import ConnectionManager
from app.modules.auction.domain.events.auction_events import (
    AuctionCancelledEvent,
    AuctionExtendedEvent,
    AuctionFinishedEvent,
    AuctionScheduledEvent,
    AuctionStartedEvent,
)
from app.modules.bidding.domain.events.bid_events import BidPlacedEvent
from app.modules.notifications.routers.notification_router import setup_notifications

# The subscriber closures live inside setup_notifications() and aren't
# exported by name, so the bus itself is the test seam: wire a real
# InMemoryEventBus + a mocked ConnectionManager, publish each event, and
# assert broadcast() got the right room/event_name/payload.


class TestNotificationRouterWiring:

    def setup_method(self):
        self.manager = AsyncMock(spec=ConnectionManager)
        self.bus = InMemoryEventBus()
        setup_notifications(manager=self.manager, bus=self.bus)

    def _assert_broadcast(self, auction_id: str, event_name: str, payload: dict) -> None:
        self.manager.broadcast.assert_called_once_with(auction_id, event_name, payload)

    async def test_bid_placed_broadcasts_to_the_auction_room(self):
        event = BidPlacedEvent(
            payload={"auction_id": "auction-1", "user_id": "u1", "amount": "150.0"}
        )

        await self.bus.publish([event])

        self._assert_broadcast("auction-1", "bidPlaced", event.payload)

    async def test_auction_started_broadcasts_to_the_auction_room(self):
        event = AuctionStartedEvent(payload={"id": "auction-1", "status": "active"})

        await self.bus.publish([event])

        self._assert_broadcast("auction-1", "auctionStarted", event.payload)

    async def test_auction_finished_broadcasts_to_the_auction_room(self):
        event = AuctionFinishedEvent(payload={"id": "auction-1", "title": "x", "end_time": ""})

        await self.bus.publish([event])

        self._assert_broadcast("auction-1", "auctionFinished", event.payload)

    async def test_auction_cancelled_broadcasts_to_the_auction_room(self):
        event = AuctionCancelledEvent(payload={"id": "auction-1", "cancelled_at": "", "reason": ""})

        await self.bus.publish([event])

        self._assert_broadcast("auction-1", "auctionCancelled", event.payload)

    async def test_auction_scheduled_broadcasts_to_the_auction_room(self):
        event = AuctionScheduledEvent(
            payload={
                "id": "auction-1",
                "start_time": "",
                "end_time": "",
                "starting_price": "100.00",
                "minimum_increment": "10.00",
            }
        )

        await self.bus.publish([event])

        self._assert_broadcast("auction-1", "auctionScheduled", event.payload)

    async def test_auction_extended_broadcasts_to_the_auction_room(self):
        event = AuctionExtendedEvent(payload={"id": "auction-1", "end_time": ""})

        await self.bus.publish([event])

        self._assert_broadcast("auction-1", "auctionExtended", event.payload)
