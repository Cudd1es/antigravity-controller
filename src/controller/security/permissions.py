"""Permission management and path security."""

import os
from pathlib import Path


class PermissionManager:
    """Manages path whitelist, user authorization, and dangerous operation tracking."""

    DANGEROUS_TOOLS = frozenset({
        "write_file", "run_command", "git_commit", "git_push",
    })

    def __init__(self, config):
        self.allowed_dirs = [Path(d).resolve() for d in config.allowed_directories]
        self.allowed_users = set(config.allowed_user_ids)
        self.require_confirmation = config.require_confirmation

    def is_path_allowed(self, path: str) -> bool:
        """Check if a path is within any allowed directory.

        Resolves symlinks and prevents path traversal attacks.
        """
        try:
            resolved = Path(path).resolve()
            return any(
                resolved == allowed or allowed in resolved.parents
                for allowed in self.allowed_dirs
            )
        except (OSError, ValueError):
            return False

    def is_user_allowed(self, user_id: str | int) -> bool:
        """Check if a Discord user ID is authorized.

        If no allowed_users configured, allow all users (single-user mode).
        """
        if not self.allowed_users:
            return True
        return str(user_id) in self.allowed_users

    def needs_confirmation(self, tool_name: str) -> bool:
        """Check if a tool operation requires user confirmation."""
        if not self.require_confirmation:
            return False
        return tool_name in self.DANGEROUS_TOOLS

    def check_tool_paths(self, tool_name: str, kwargs: dict) -> str | None:
        """Validate all path arguments in a tool call.

        Returns an error message if any path is not allowed, or None if all OK.
        """
        path_keys = ["path", "repo_path", "directory", "cwd"]
        for key in path_keys:
            if key in kwargs:
                p = kwargs[key]
                if not self.is_path_allowed(p):
                    return (
                        f"Access denied: '{p}' is outside allowed directories. "
                        f"Allowed: {[str(d) for d in self.allowed_dirs]}"
                    )
                # Also check that path doesn't contain suspicious patterns
                if ".." in os.path.normpath(p):
                    return f"Access denied: path traversal detected in '{p}'"
        return None
