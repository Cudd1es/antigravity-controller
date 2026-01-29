"""
Pydantic models for agent status and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentState(str, Enum):
    """Possible states of the agent."""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentStatus(BaseModel):
    """Current status of the agent."""

    agent_id: str = Field(description="Unique agent identifier")
    state: AgentState = Field(description="Current agent state")
    current_task: Optional[str] = Field(default=None, description="Currently executing task")
    last_active: datetime = Field(description="Last activity timestamp")
    version: Optional[str] = Field(default=None, description="Agent version")


class TaskResult(BaseModel):
    """Result of a completed task."""

    task_id: str = Field(description="Unique task identifier")
    command_id: str = Field(description="Associated command identifier")
    success: bool = Field(description="Whether the task succeeded")
    result: Optional[Any] = Field(default=None, description="Task result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: float = Field(description="Execution time in seconds")
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
