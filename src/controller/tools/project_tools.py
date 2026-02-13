"""Project structure and metadata tools."""

import os
from typing import Any

import aiofiles

from controller.tools.base import Tool


class ProjectStructureTool(Tool):
    """Display project directory tree."""

    @property
    def name(self) -> str:
        return "get_project_structure"

    @property
    def description(self) -> str:
        return "Display the directory tree structure of a project, showing files and folders."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the project root directory",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to display (default: 3)",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        max_depth = kwargs.get("max_depth", 3)

        if not os.path.isdir(path):
            return f"Error: Not a directory: {path}"

        lines = [f"{os.path.basename(path)}/"]
        self._build_tree(path, lines, "", max_depth, 0)

        if len(lines) > 150:
            lines = lines[:150]
            lines.append("... (truncated)")

        return "\n".join(lines)

    def _build_tree(
        self, path: str, lines: list[str], prefix: str, max_depth: int, depth: int
    ) -> None:
        if depth >= max_depth:
            return

        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return

        # Filter hidden files/dirs and common noise
        skip = {".git", ".venv", "venv", "__pycache__", "node_modules", ".DS_Store", ".eggs"}
        entries = [e for e in entries if e not in skip and not e.startswith(".")]

        for i, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            is_last = i == len(entries) - 1
            connector = "+-" if is_last else "|-"
            extension = "  " if is_last else "| "

            if os.path.isdir(full_path):
                lines.append(f"{prefix}{connector} {entry}/")
                self._build_tree(full_path, lines, prefix + extension, max_depth, depth + 1)
            else:
                size = os.path.getsize(full_path)
                size_str = self._format_size(size)
                lines.append(f"{prefix}{connector} {entry} ({size_str})")

    @staticmethod
    def _format_size(size: int) -> str:
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        else:
            return f"{size / (1024 * 1024):.1f}MB"


class FileInfoTool(Tool):
    """Get metadata about a file."""

    @property
    def name(self) -> str:
        return "get_file_info"

    @property
    def description(self) -> str:
        return "Get metadata about a file: size, last modified time, line count, etc."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the file",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        if not os.path.exists(path):
            return f"Error: Path does not exist: {path}"

        stat = os.stat(path)
        info = [
            f"Path: {path}",
            f"Type: {'directory' if os.path.isdir(path) else 'file'}",
            f"Size: {ProjectStructureTool._format_size(stat.st_size)}",
        ]

        if os.path.isfile(path):
            try:
                async with aiofiles.open(path, "r", encoding="utf-8") as f:
                    content = await f.read()
                info.append(f"Lines: {content.count(chr(10)) + 1}")
                info.append(f"Extension: {os.path.splitext(path)[1] or 'none'}")
            except (UnicodeDecodeError, PermissionError):
                info.append("Content: binary or unreadable")

        return "\n".join(info)


class FindTodosTool(Tool):
    """Search for TODO and FIXME comments in project files."""

    @property
    def name(self) -> str:
        return "find_todos"

    @property
    def description(self) -> str:
        return "Search for TODO, FIXME, HACK, and XXX comments in project source files."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the project directory to search",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        if not os.path.isdir(path):
            return f"Error: Not a directory: {path}"

        markers = ["TODO", "FIXME", "HACK", "XXX"]
        skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules"}
        results = []

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for filename in sorted(files):
                if not any(filename.endswith(ext) for ext in [".py", ".js", ".ts", ".go", ".rs", ".java", ".md"]):
                    continue
                filepath = os.path.join(root, filename)
                try:
                    async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                        lines = await f.readlines()
                    for i, line in enumerate(lines, 1):
                        upper = line.upper()
                        for marker in markers:
                            if marker in upper:
                                rel = os.path.relpath(filepath, path)
                                results.append(f"[{marker}] {rel}:{i}: {line.strip()}")
                                break
                except (UnicodeDecodeError, PermissionError):
                    continue

                if len(results) >= 50:
                    results.append("... (results truncated)")
                    return "\n".join(results)

        if not results:
            return "No TODO/FIXME/HACK/XXX comments found"
        return "\n".join(results)
