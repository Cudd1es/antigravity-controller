"""Git operations tools."""

import asyncio
from typing import Any

from controller.tools.base import Tool


async def _run_git(args: list[str], cwd: str, timeout: int = 15) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    proc = await asyncio.create_subprocess_exec(
        "git", *args,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return -1, "", "Command timed out"
    return proc.returncode, stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace")


class GitStatusTool(Tool):
    """Show git status of a repository."""

    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Show the git status of a repository (modified, staged, untracked files)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Absolute path to the git repository",
                },
            },
            "required": ["repo_path"],
        }

    async def execute(self, **kwargs) -> str:
        repo_path = kwargs["repo_path"]
        code, stdout, stderr = await _run_git(["status", "--short", "--branch"], repo_path)
        if code != 0:
            return f"Error: {stderr.strip()}"
        return stdout.strip() if stdout.strip() else "Working tree is clean"


class GitDiffTool(Tool):
    """Show git diff."""

    @property
    def name(self) -> str:
        return "git_diff"

    @property
    def description(self) -> str:
        return "Show the git diff of uncommitted changes in a repository."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Absolute path to the git repository",
                },
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes only (default: false)",
                },
            },
            "required": ["repo_path"],
        }

    async def execute(self, **kwargs) -> str:
        repo_path = kwargs["repo_path"]
        staged = kwargs.get("staged", False)
        args = ["diff", "--stat"]
        if staged:
            args.append("--cached")
        code, stdout, stderr = await _run_git(args, repo_path)
        if code != 0:
            return f"Error: {stderr.strip()}"
        if not stdout.strip():
            return "No changes" + (" staged" if staged else "")

        # Also get the actual diff but truncated
        detail_args = ["diff"]
        if staged:
            detail_args.append("--cached")
        _, detail_out, _ = await _run_git(detail_args, repo_path)
        # Truncate long diffs
        lines = detail_out.split("\n")
        if len(lines) > 100:
            detail_out = "\n".join(lines[:100]) + f"\n\n... ({len(lines) - 100} more lines)"
        return f"Summary:\n{stdout.strip()}\n\nDiff:\n{detail_out.strip()}"


class GitLogTool(Tool):
    """Show git log."""

    @property
    def name(self) -> str:
        return "git_log"

    @property
    def description(self) -> str:
        return "Show recent git commit history."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Absolute path to the git repository",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of commits to show (default: 10, max: 30)",
                },
            },
            "required": ["repo_path"],
        }

    async def execute(self, **kwargs) -> str:
        repo_path = kwargs["repo_path"]
        count = min(kwargs.get("count", 10), 30)
        code, stdout, stderr = await _run_git(
            ["log", f"-{count}", "--oneline", "--decorate"], repo_path
        )
        if code != 0:
            return f"Error: {stderr.strip()}"
        return stdout.strip() if stdout.strip() else "No commits yet"


class GitCommitTool(Tool):
    """Create a git commit."""

    @property
    def name(self) -> str:
        return "git_commit"

    @property
    def description(self) -> str:
        return "Stage all changes and create a git commit with the given message."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Absolute path to the git repository",
                },
                "message": {
                    "type": "string",
                    "description": "Commit message",
                },
            },
            "required": ["repo_path", "message"],
        }

    @property
    def dangerous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> str:
        repo_path = kwargs["repo_path"]
        message = kwargs["message"]
        # Stage all changes
        code, _, stderr = await _run_git(["add", "-A"], repo_path)
        if code != 0:
            return f"Error staging files: {stderr.strip()}"
        # Commit
        code, stdout, stderr = await _run_git(["commit", "-m", message], repo_path)
        if code != 0:
            return f"Error committing: {stderr.strip()}"
        return stdout.strip()


class GitPushTool(Tool):
    """Push commits to remote."""

    @property
    def name(self) -> str:
        return "git_push"

    @property
    def description(self) -> str:
        return "Push committed changes to the remote repository."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Absolute path to the git repository",
                },
            },
            "required": ["repo_path"],
        }

    @property
    def dangerous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> str:
        repo_path = kwargs["repo_path"]
        code, stdout, stderr = await _run_git(["push"], repo_path, timeout=30)
        if code != 0:
            return f"Error pushing: {stderr.strip()}"
        output = stdout.strip() or stderr.strip()  # git push often uses stderr for info
        return output if output else "Push successful"
