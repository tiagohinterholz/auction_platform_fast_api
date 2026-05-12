from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self._rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, auction_id: str) -> None:
        await websocket.accept()
        self._rooms.setdefault(auction_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, auction_id: str) -> None:
        if auction_id in self._rooms:
            self._rooms[auction_id].remove(websocket)
            if not self._rooms[auction_id]:
                del self._rooms[auction_id]

    async def broadcast(self, auction_id: str, event_name: str, payload: dict) -> None:
        for connections in self._rooms.get(auction_id, []):
            await connections.send_json({"event": event_name, "payload": payload})

manager = ConnectionManager()