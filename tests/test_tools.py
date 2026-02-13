"""Tests for local tool implementations."""

import os

import pytest

from controller.tools.file_tools import (
    ListDirectoryTool,
    ReadFileTool,
    SearchInFilesTool,
    WriteFileTool,
)
from controller.tools.git_tools import GitLogTool, GitStatusTool
from controller.tools.project_tools import FileInfoTool, FindTodosTool, ProjectStructureTool


class TestReadFileTool:
    @pytest.fixture
    def tool(self):
        return ReadFileTool()

    @pytest.mark.asyncio
    async def test_read_existing_file(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project / "README.md"))
        assert "Test Project" in result
        assert "lines" in result

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project / "missing.txt"))
        assert "Error" in result
        assert "not found" in result


class TestWriteFileTool:
    @pytest.fixture
    def tool(self):
        return WriteFileTool()

    @pytest.mark.asyncio
    async def test_write_new_file(self, tool, tmp_project):
        path = str(tmp_project / "newfile.txt")
        result = await tool.execute(path=path, content="hello world")
        assert "Successfully" in result
        assert os.path.exists(path)
        with open(path) as f:
            assert f.read() == "hello world"

    @pytest.mark.asyncio
    async def test_write_creates_directories(self, tool, tmp_project):
        path = str(tmp_project / "sub" / "dir" / "file.txt")
        result = await tool.execute(path=path, content="nested")
        assert "Successfully" in result
        assert os.path.exists(path)

    def test_is_dangerous(self, tool):
        assert tool.dangerous is True


class TestListDirectoryTool:
    @pytest.fixture
    def tool(self):
        return ListDirectoryTool()

    @pytest.mark.asyncio
    async def test_list_directory(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project))
        assert "README.md" in result
        assert "src/" in result

    @pytest.mark.asyncio
    async def test_list_nonexistent(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project / "nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_list_recursive(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project), recursive=True)
        assert "main.py" in result
        assert "utils.py" in result


class TestSearchInFilesTool:
    @pytest.fixture
    def tool(self):
        return SearchInFilesTool()

    @pytest.mark.asyncio
    async def test_search_found(self, tool, tmp_project):
        result = await tool.execute(directory=str(tmp_project), pattern="helper")
        assert "utils.py" in result
        assert "helper" in result

    @pytest.mark.asyncio
    async def test_search_not_found(self, tool, tmp_project):
        result = await tool.execute(directory=str(tmp_project), pattern="nonexistent_xyz")
        assert "No matches" in result

    @pytest.mark.asyncio
    async def test_search_with_extension(self, tool, tmp_project):
        result = await tool.execute(
            directory=str(tmp_project), pattern="pass", file_extension=".py"
        )
        assert "main.py" in result


class TestProjectStructureTool:
    @pytest.fixture
    def tool(self):
        return ProjectStructureTool()

    @pytest.mark.asyncio
    async def test_structure(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project))
        assert "src/" in result
        assert "README.md" in result


class TestFileInfoTool:
    @pytest.fixture
    def tool(self):
        return FileInfoTool()

    @pytest.mark.asyncio
    async def test_file_info(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project / "README.md"))
        assert "Lines:" in result
        assert "file" in result


class TestFindTodosTool:
    @pytest.fixture
    def tool(self):
        return FindTodosTool()

    @pytest.mark.asyncio
    async def test_find_todos(self, tool, tmp_project):
        result = await tool.execute(path=str(tmp_project))
        assert "TODO" in result
        assert "main.py" in result
