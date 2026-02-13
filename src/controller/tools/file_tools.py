"""File system tools for reading, writing, and searching files."""

import os
from typing import Any

import aiofiles

from controller.tools.base import Tool


class ReadFileTool(Tool):
    """Read the contents of a file."""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file at the given path. Returns the file content as text."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the file to read",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()
            line_count = content.count("\n") + 1
            return f"File: {path} ({line_count} lines)\n\n{content}"
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except UnicodeDecodeError:
            return f"Error: Cannot read binary file: {path}"
        except Exception as e:
            return f"Error reading file: {e}"


class WriteFileTool(Tool):
    """Write content to a file."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Write content to a file. Creates the file and parent directories if they don't exist. "
            "Overwrites existing content."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        }

    @property
    def dangerous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        content = kwargs["content"]
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(content)
            return f"Successfully wrote {len(content)} characters to {path}"
        except Exception as e:
            return f"Error writing file: {e}"


class ListDirectoryTool(Tool):
    """List contents of a directory."""

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "List files and subdirectories in the given directory path."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the directory to list",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "If true, list recursively (default: false)",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        recursive = kwargs.get("recursive", False)
        try:
            if not os.path.isdir(path):
                return f"Error: Not a directory: {path}"

            entries = []
            if recursive:
                for root, dirs, files in os.walk(path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                    level = root.replace(path, "").count(os.sep)
                    indent = "  " * level
                    basename = os.path.basename(root)
                    if level > 0:
                        entries.append(f"{indent}{basename}/")
                    for f in sorted(files):
                        if not f.startswith("."):
                            entries.append(f"{indent}  {f}")
                    if level > 3:  # Limit depth
                        dirs.clear()
            else:
                items = sorted(os.listdir(path))
                for item in items:
                    if item.startswith("."):
                        continue
                    full = os.path.join(path, item)
                    suffix = "/" if os.path.isdir(full) else ""
                    entries.append(f"  {item}{suffix}")

            if not entries:
                return f"Directory {path} is empty"

            header = f"Contents of {path}:\n"
            return header + "\n".join(entries[:200])  # Cap output
        except Exception as e:
            return f"Error listing directory: {e}"


class SearchInFilesTool(Tool):
    """Search for a pattern in files within a directory."""

    @property
    def name(self) -> str:
        return "search_in_files"

    @property
    def description(self) -> str:
        return (
            "Search for a text pattern in files within a directory. "
            "Returns matching lines with file paths and line numbers."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Absolute path to the directory to search in",
                },
                "pattern": {
                    "type": "string",
                    "description": "Text pattern to search for",
                },
                "file_extension": {
                    "type": "string",
                    "description": "Optional file extension filter (e.g., '.py', '.js')",
                },
            },
            "required": ["directory", "pattern"],
        }

    async def execute(self, **kwargs) -> str:
        directory = kwargs["directory"]
        pattern = kwargs["pattern"]
        ext_filter = kwargs.get("file_extension", "")

        if not os.path.isdir(directory):
            return f"Error: Not a directory: {directory}"

        matches = []
        try:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for filename in sorted(files):
                    if filename.startswith("."):
                        continue
                    if ext_filter and not filename.endswith(ext_filter):
                        continue
                    filepath = os.path.join(root, filename)
                    try:
                        async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                            lines = await f.readlines()
                        for i, line in enumerate(lines, 1):
                            if pattern.lower() in line.lower():
                                rel_path = os.path.relpath(filepath, directory)
                                matches.append(f"{rel_path}:{i}: {line.rstrip()}")
                                if len(matches) >= 50:  # Cap results
                                    matches.append("... (results truncated)")
                                    return "\n".join(matches)
                    except (UnicodeDecodeError, PermissionError):
                        continue

            if not matches:
                return f"No matches found for '{pattern}' in {directory}"
            return "\n".join(matches)
        except Exception as e:
            return f"Error searching files: {e}"
