"""Shell command execution tool with timeout and output truncation."""

import asyncio
from typing import Any

from controller.tools.base import Tool


class RunCommandTool(Tool):
    """Execute a shell command."""

    def __init__(self, timeout: int = 30):
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return (
            "Execute a shell command in the given working directory. "
            "Use this for running tests, builds, linters, or other CLI tools. "
            "The command will be terminated after a timeout."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory for the command",
                },
            },
            "required": ["command", "cwd"],
        }

    @property
    def dangerous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> str:
        command = kwargs["command"]
        cwd = kwargs["cwd"]

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=None,  # Inherit current environment
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=self._timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return f"Command timed out after {self._timeout}s: {command}"

            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            # Truncate long output
            max_chars = 3000
            if len(stdout_text) > max_chars:
                stdout_text = stdout_text[:max_chars] + "\n... (output truncated)"
            if len(stderr_text) > max_chars:
                stderr_text = stderr_text[:max_chars] + "\n... (stderr truncated)"

            parts = [f"Exit code: {proc.returncode}"]
            if stdout_text.strip():
                parts.append(f"stdout:\n{stdout_text.strip()}")
            if stderr_text.strip():
                parts.append(f"stderr:\n{stderr_text.strip()}")

            return "\n\n".join(parts)
        except Exception as e:
            return f"Error executing command: {e}"
