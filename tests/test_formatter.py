"""Tests for Discord message formatter."""

import pytest

from controller.bot.formatter import (
    format_code_block,
    format_error,
    format_success,
    split_message,
    truncate,
)


class TestSplitMessage:
    def test_short_message(self):
        result = split_message("hello")
        assert result == ["hello"]

    def test_long_message_splits(self):
        text = "a" * 3000
        result = split_message(text, max_length=1900)
        assert len(result) == 2
        # All content should be preserved
        combined = "".join(result)
        assert len(combined) == 3000

    def test_splits_at_newline(self):
        text = "line1\n" * 400  # ~2400 chars
        result = split_message(text, max_length=1900)
        assert len(result) == 2
        # Each chunk should end/start cleanly
        assert not result[0].endswith("\n\n")

    def test_preserves_code_blocks(self):
        text = "before\n```python\n" + "x = 1\n" * 500 + "```\nafter"
        result = split_message(text, max_length=1900)
        assert len(result) >= 2
        # Split code blocks should be closed and reopened
        for i, chunk in enumerate(result):
            opens = chunk.count("```")
            # Each chunk should have balanced code blocks
            assert opens % 2 == 0, f"Chunk {i} has unbalanced code blocks"


class TestFormatCodeBlock:
    def test_with_language(self):
        result = format_code_block("print('hi')", "python")
        assert result == "```python\nprint('hi')\n```"

    def test_without_language(self):
        result = format_code_block("some text")
        assert result == "```\nsome text\n```"


class TestFormatError:
    def test_error_format(self):
        assert format_error("something broke") == "**Error:** something broke"


class TestFormatSuccess:
    def test_success_format(self):
        assert format_success("all good") == "**Done:** all good"


class TestTruncate:
    def test_short_text(self):
        assert truncate("hi", 100) == "hi"

    def test_long_text(self):
        long = "x" * 2000
        result = truncate(long, 100)
        assert len(result) == 100
        assert result.endswith("(truncated)")
