from unittest.mock import AsyncMock

from app.core.websockets.connection_manager import ConnectionManager


class TestConnectionManager:

    async def test_broadcast_reaches_connections_in_the_same_room(self):
        manager = ConnectionManager()
        ws = AsyncMock()
        await manager.connect(ws, "auction-1")

        await manager.broadcast("auction-1", "bidPlaced", {"amount": "150.00"})

        ws.accept.assert_awaited_once()
        ws.send_json.assert_awaited_once_with(
            {"event": "bidPlaced", "payload": {"amount": "150.00"}}
        )

    async def test_broadcast_does_not_reach_other_rooms(self):
        manager = ConnectionManager()
        ws = AsyncMock()
        await manager.connect(ws, "auction-1")

        await manager.broadcast("auction-2", "bidPlaced", {"amount": "150.00"})

        ws.send_json.assert_not_awaited()

    async def test_broadcast_reaches_every_connection_in_the_room(self):
        manager = ConnectionManager()
        ws_a, ws_b = AsyncMock(), AsyncMock()
        await manager.connect(ws_a, "auction-1")
        await manager.connect(ws_b, "auction-1")

        await manager.broadcast("auction-1", "auctionStarted", {})

        ws_a.send_json.assert_awaited_once()
        ws_b.send_json.assert_awaited_once()

    async def test_disconnect_stops_further_broadcasts_reaching_it(self):
        manager = ConnectionManager()
        ws = AsyncMock()
        await manager.connect(ws, "auction-1")

        manager.disconnect(ws, "auction-1")
        await manager.broadcast("auction-1", "bidPlaced", {})

        ws.send_json.assert_not_awaited()

    async def test_disconnect_removes_the_room_once_it_is_empty(self):
        manager = ConnectionManager()
        ws = AsyncMock()
        await manager.connect(ws, "auction-1")

        manager.disconnect(ws, "auction-1")

        assert "auction-1" not in manager._rooms
