"""
Status API endpoints.
"""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from controller.models import AgentState, AgentStatus
from controller.services.agent_client import agent_client

router = APIRouter()


class SystemStatus(BaseModel):
    """Overall system status."""

    controller_status: str
    agent_status: AgentStatus | None
    timestamp: datetime


@router.get("/agent/status", response_model=AgentStatus | None)
async def get_agent_status() -> AgentStatus | None:
    """Get current agent status."""
    return await agent_client.get_status()


@router.get("/status", response_model=SystemStatus)
async def get_system_status() -> SystemStatus:
    """Get overall system status including controller and agent."""
    agent_status = await agent_client.get_status()

    return SystemStatus(
        controller_status="online",
        agent_status=agent_status,
        timestamp=datetime.utcnow(),
    )
