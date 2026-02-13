"""Pytest fixtures."""

import os
import tempfile

import pytest

from controller.config import Config


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with sample files."""
    # Create project structure
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "main.py").write_text("# TODO: implement main\ndef main():\n    pass\n")
    (src / "utils.py").write_text("def helper():\n    return 42\n")

    readme = tmp_path / "README.md"
    readme.write_text("# Test Project\n\nA sample project.\n")

    return tmp_path


@pytest.fixture
def config(tmp_project):
    """Create a test Config."""
    return Config(
        discord_token="test-token",
        discord_guild_id="123456",
        gemini_api_key="test-key",
        gemini_model="gemini-2.5-flash",
        allowed_directories=[str(tmp_project)],
        allowed_user_ids=["111222333"],
        max_file_size_kb=500,
        command_timeout_seconds=10,
        require_confirmation=True,
    )
