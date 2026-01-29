"""
HTTP client for communicating with remote Antigravity Agent.
"""

from datetime import datetime
from typing import Optional

import httpx

from controller.config import get_settings
from controller.models import AgentState, AgentStatus


class AgentClient:
    """Client for communicating with the remote Antigravity Agent."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.agent_base_url
        self.api_key = self.settings.agent_api_key

    def _get_headers(self) -> dict[str, str]:
        """Get request headers including authentication."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def get_status(self) -> Optional[AgentStatus]:
        """Get current agent status."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/status",
                    headers=self._get_headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    return AgentStatus(
                        agent_id=data.get("agent_id", "unknown"),
                        state=AgentState(data.get("state", "offline")),
                        current_task=data.get("current_task"),
                        last_active=datetime.fromisoformat(
                            data.get("last_active", datetime.utcnow().isoformat())
                        ),
                        version=data.get("version"),
                    )
        except Exception:
            pass

        # Return offline status if agent is unreachable
        return AgentStatus(
            agent_id="unknown",
            state=AgentState.OFFLINE,
            current_task=None,
            last_active=datetime.utcnow(),
            version=None,
        )

    async def send_command(
        self, command_id: str, command_type: str, content: str, metadata: Optional[dict] = None
    ) -> bool:
        """Send a command to the agent for execution."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/execute",
                    headers=self._get_headers(),
                    json={
                        "command_id": command_id,
                        "type": command_type,
                        "content": content,
                        "metadata": metadata or {},
                    },
                )
                return response.status_code in [200, 201, 202]
        except Exception:
            return False

    async def cancel_task(self, task_id: str) -> bool:
        """Request the agent to cancel a running task."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/cancel",
                    headers=self._get_headers(),
                    json={"task_id": task_id},
                )
                return response.status_code == 200
        except Exception:
            return False

    async def health_check(self) -> bool:
        """Check if the agent is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._get_headers(),
                )
                return response.status_code == 200
        except Exception:
            return False


# Global agent client instance
agent_client = AgentClient()
