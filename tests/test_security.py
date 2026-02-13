"""Tests for the security/permissions module."""

import pytest

from controller.config import Config
from controller.security.permissions import PermissionManager


@pytest.fixture
def manager(config):
    return PermissionManager(config)


class TestPathPermissions:
    def test_allowed_path(self, manager, tmp_project):
        assert manager.is_path_allowed(str(tmp_project / "src" / "main.py")) is True

    def test_disallowed_path(self, manager):
        assert manager.is_path_allowed("/etc/passwd") is False

    def test_path_traversal(self, manager, tmp_project):
        # Attempting to traverse out of allowed directory
        evil_path = str(tmp_project / ".." / ".." / "etc" / "passwd")
        assert manager.is_path_allowed(evil_path) is False

    def test_nonexistent_but_within_allowed(self, manager, tmp_project):
        # Path doesn't exist yet but is within allowed dir
        assert manager.is_path_allowed(str(tmp_project / "new" / "file.py")) is True


class TestUserPermissions:
    def test_allowed_user(self, manager):
        assert manager.is_user_allowed("111222333") is True

    def test_disallowed_user(self, manager):
        assert manager.is_user_allowed("999999999") is False

    def test_no_user_restriction(self, tmp_project):
        config = Config(
            discord_token="t",
            allowed_directories=[str(tmp_project)],
            allowed_user_ids=[],
        )
        m = PermissionManager(config)
        assert m.is_user_allowed("anyone") is True


class TestDangerousOperations:
    def test_dangerous_tools(self, manager):
        assert manager.needs_confirmation("write_file") is True
        assert manager.needs_confirmation("run_command") is True
        assert manager.needs_confirmation("git_commit") is True
        assert manager.needs_confirmation("git_push") is True

    def test_safe_tools(self, manager):
        assert manager.needs_confirmation("read_file") is False
        assert manager.needs_confirmation("list_directory") is False
        assert manager.needs_confirmation("git_status") is False

    def test_confirmation_disabled(self, tmp_project):
        config = Config(
            discord_token="t",
            allowed_directories=[str(tmp_project)],
            require_confirmation=False,
        )
        m = PermissionManager(config)
        assert m.needs_confirmation("write_file") is False


class TestToolPathChecking:
    def test_allowed_tool_path(self, manager, tmp_project):
        result = manager.check_tool_paths("read_file", {"path": str(tmp_project / "f.py")})
        assert result is None

    def test_disallowed_tool_path(self, manager):
        result = manager.check_tool_paths("read_file", {"path": "/etc/passwd"})
        assert result is not None
        assert "Access denied" in result

    def test_repo_path_key(self, manager, tmp_project):
        result = manager.check_tool_paths("git_status", {"repo_path": str(tmp_project)})
        assert result is None

    def test_cwd_key(self, manager, tmp_project):
        result = manager.check_tool_paths("run_command", {"cwd": str(tmp_project), "command": "ls"})
        assert result is None
