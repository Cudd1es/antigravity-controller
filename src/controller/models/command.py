"""
Pydantic models for commands and requests.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class CommandType(str, Enum):
    """Types of commands that can be sent to the agent."""

    QUERY = "query"
    ACTION = "action"
    CONFIG = "config"


class CommandStatus(str, Enum):
    """Status of a command execution."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CommandCreate(BaseModel):
    """Request model for creating a new command."""

    type: CommandType = Field(description="Type of command")
    content: str = Field(description="Command content or instruction")
    priority: int = Field(default=0, ge=0, le=10, description="Priority level (0-10)")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Additional metadata")


class Command(BaseModel):
    """Full command model with all fields."""

    id: str = Field(description="Unique command identifier")
    type: CommandType
    content: str
    priority: int = 0
    status: CommandStatus = CommandStatus.PENDING
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommandResponse(BaseModel):
    """Response model for command operations."""

    id: str
    status: CommandStatus
    message: str
