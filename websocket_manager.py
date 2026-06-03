from __future__ import annotations

import json
from collections import defaultdict

from fastapi import WebSocket

class ConnectionManager:
    """
    Manages active WebSocket connections grouped by post_id.
    Each post has its own set of connected clients; broadcasting
    a new comment only fans out to viewers of that specific post.
    """

    def __init__(self) -> None:
        # post_id -> set of active WebSocket connections
        self._rooms: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, post_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms[post_id].add(websocket)

    def disconnect(self, post_id: int, websocket: WebSocket) -> None:
        self._rooms[post_id].discard(websocket)
        if not self._rooms[post_id]:
            del self._rooms[post_id]

    async def broadcast(self, post_id: int, payload: dict) -> None:
        """
        Send a JSON payload to every client currently viewing post_id.
        Dead connections are collected and removed so they don't
        accumulate silently.
        """
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(post_id, [])):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(post_id, ws)


# instance 
manager = ConnectionManager()

#for notifs-unicast 
class NotificationManager:
    """
    Manages per-user WebSocket connections for personal notifications.
    e.g. "someone commented on your post"
    """

    def __init__(self) -> None:
        # user_id -> set of active WebSocket connections
        self._users: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._users[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        self._users[user_id].discard(websocket)
        if not self._users[user_id]:
            del self._users[user_id]

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        """Send a notification to a specific user across all their tabs."""
        dead: list[WebSocket] = []
        for ws in list(self._users.get(user_id, [])):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)


notification_manager = NotificationManager()