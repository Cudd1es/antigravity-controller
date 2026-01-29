"""
WebSocket router and endpoints.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from controller.models import WSMessage, WSMessageType
from controller.websocket.manager import connection_manager

router = APIRouter()


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    
    Message types:
    - Server to Client: agent_status, task_progress, task_result, error, heartbeat
    - Client to Server: subscribe, unsubscribe, ping
    """
    client_id = str(uuid.uuid4())

    await connection_manager.connect(websocket, client_id)

    # Send welcome message
    welcome_message = WSMessage(
        type=WSMessageType.HEARTBEAT,
        payload={"client_id": client_id, "message": "Connected to Antigravity Controller"},
        timestamp=datetime.utcnow(),
    )
    await connection_manager.send_message(client_id, welcome_message)

    try:
        while True:
            # Receive and parse message from client
            data = await websocket.receive_json()

            message_type = data.get("type", "")

            if message_type == WSMessageType.PING.value:
                # Respond to ping with heartbeat
                response = WSMessage(
                    type=WSMessageType.HEARTBEAT,
                    payload={"pong": True},
                    timestamp=datetime.utcnow(),
                )
                await connection_manager.send_message(client_id, response)

            elif message_type == WSMessageType.SUBSCRIBE.value:
                # Handle subscription requests
                topics = data.get("payload", {}).get("topics", [])
                response = WSMessage(
                    type=WSMessageType.HEARTBEAT,
                    payload={"subscribed": topics},
                    timestamp=datetime.utcnow(),
                )
                await connection_manager.send_message(client_id, response)

            elif message_type == WSMessageType.UNSUBSCRIBE.value:
                # Handle unsubscription requests
                topics = data.get("payload", {}).get("topics", [])
                response = WSMessage(
                    type=WSMessageType.HEARTBEAT,
                    payload={"unsubscribed": topics},
                    timestamp=datetime.utcnow(),
                )
                await connection_manager.send_message(client_id, response)

    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
    except Exception as e:
        # Send error message before disconnecting
        error_message = WSMessage(
            type=WSMessageType.ERROR,
            payload={"code": 500, "message": str(e)},
            timestamp=datetime.utcnow(),
        )
        try:
            await connection_manager.send_message(client_id, error_message)
        except Exception:
            pass
        connection_manager.disconnect(client_id)
