"""Discord message formatting utilities.

Handles Discord's 2000-character message limit and code block formatting.
"""


def split_message(text: str, max_length: int = 1900) -> list[str]:
    """Split a long message into chunks that fit Discord's limit.

    Tries to split at natural boundaries: code blocks, newlines, spaces.
    Preserves code block formatting across splits.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        # Try to find a good split point
        split_at = _find_split_point(remaining, max_length)
        chunk = remaining[:split_at].rstrip()
        remaining = remaining[split_at:].lstrip("\n")

        # Handle code blocks that might be split
        if chunk.count("```") % 2 != 0:
            # Odd number of ``` means we're inside a code block
            chunk += "\n```"
            remaining = "```\n" + remaining

        chunks.append(chunk)

    return chunks if chunks else [""]


def _find_split_point(text: str, max_length: int) -> int:
    """Find the best position to split text at."""
    # Try splitting at a code block boundary
    last_block = text.rfind("```\n", 0, max_length)
    if last_block > max_length // 2:
        # Find the end of this code block line
        newline_after = text.find("\n", last_block + 3)
        if newline_after != -1 and newline_after <= max_length:
            return newline_after + 1

    # Try splitting at a blank line
    last_blank = text.rfind("\n\n", 0, max_length)
    if last_blank > max_length // 2:
        return last_blank + 1

    # Try splitting at a newline
    last_newline = text.rfind("\n", 0, max_length)
    if last_newline > max_length // 3:
        return last_newline + 1

    # Try splitting at a space
    last_space = text.rfind(" ", 0, max_length)
    if last_space > max_length // 3:
        return last_space + 1

    # Hard split
    return max_length


def format_code_block(content: str, language: str = "") -> str:
    """Wrap content in a Discord code block with optional language tag."""
    return f"```{language}\n{content}\n```"


def format_error(message: str) -> str:
    """Format an error message."""
    return f"**Error:** {message}"


def format_success(message: str) -> str:
    """Format a success message."""
    return f"**Done:** {message}"


def truncate(text: str, max_length: int = 1800, suffix: str = "\n... (truncated)") -> str:
    """Truncate text to max_length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
