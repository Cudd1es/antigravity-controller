"""
WebSocket connection manager for real-time communication.
"""

from datetime import datetime
from typing import Any

from fastapi import WebSocket

from controller.models import WSMessage, WSMessageType


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: WSMessage):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message.model_dump(mode="json"))

    async def broadcast(self, message: WSMessage):
        """Broadcast a message to all connected clients."""
        for client_id in list(self.active_connections.keys()):
            try:
                await self.send_message(client_id, message)
            except Exception:
                # Client disconnected, remove from active connections
                self.disconnect(client_id)

    async def broadcast_agent_status(self, status: dict[str, Any]):
        """Broadcast agent status update."""
        message = WSMessage(
            type=WSMessageType.AGENT_STATUS,
            payload=status,
            timestamp=datetime.utcnow(),
        )
        await self.broadcast(message)

    async def broadcast_task_progress(self, task_id: str, progress: float, details: str):
        """Broadcast task progress update."""
        message = WSMessage(
            type=WSMessageType.TASK_PROGRESS,
            payload={
                "task_id": task_id,
                "progress": progress,
                "details": details,
            },
            timestamp=datetime.utcnow(),
        )
        await self.broadcast(message)

    async def broadcast_task_result(self, task_id: str, result: dict[str, Any]):
        """Broadcast task result."""
        message = WSMessage(
            type=WSMessageType.TASK_RESULT,
            payload={
                "task_id": task_id,
                "result": result,
            },
            timestamp=datetime.utcnow(),
        )
        await self.broadcast(message)

    async def broadcast_command_created(self, command_id: str, command_type: str):
        """Broadcast that a new command was created."""
        message = WSMessage(
            type=WSMessageType.TASK_PROGRESS,
            payload={
                "command_id": command_id,
                "command_type": command_type,
                "event": "command_created",
            },
            timestamp=datetime.utcnow(),
        )
        await self.broadcast(message)

    async def broadcast_error(self, error_code: int, error_message: str):
        """Broadcast an error to all clients."""
        message = WSMessage(
            type=WSMessageType.ERROR,
            payload={
                "code": error_code,
                "message": error_message,
            },
            timestamp=datetime.utcnow(),
        )
        await self.broadcast(message)

    @property
    def connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
connection_manager = ConnectionManager()
