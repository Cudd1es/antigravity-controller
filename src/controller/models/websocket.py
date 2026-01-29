"""
Pydantic models for WebSocket messages.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WSMessageType(str, Enum):
    """Types of WebSocket messages."""

    # Server to client
    AGENT_STATUS = "agent_status"
    TASK_PROGRESS = "task_progress"
    TASK_RESULT = "task_result"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

    # Client to server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"


class WSMessage(BaseModel):
    """WebSocket message structure."""

    type: WSMessageType = Field(description="Message type")
    payload: Any = Field(description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WSError(BaseModel):
    """WebSocket error message."""

    code: int = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Any = None
