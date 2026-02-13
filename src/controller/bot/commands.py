"""Discord slash commands for bot management."""

import discord
from discord import app_commands
from discord.ext import commands


def setup_commands(bot: commands.Bot) -> None:
    """Register slash commands with the bot."""

    @bot.tree.command(name="status", description="Show bot and project status")
    async def status_command(interaction: discord.Interaction):
        allowed_dirs = bot.config.allowed_directories
        dirs_list = "\n".join(f"  - `{d}`" for d in allowed_dirs) if allowed_dirs else "  None"

        embed = discord.Embed(
            title="Antigravity Controller Status",
            color=discord.Color.green(),
        )
        embed.add_field(name="Model", value=f"`{bot.config.gemini_model}`", inline=True)
        embed.add_field(
            name="Confirmation",
            value="Enabled" if bot.config.require_confirmation else "Disabled",
            inline=True,
        )
        embed.add_field(name="Allowed Directories", value=dirs_list, inline=False)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="clear", description="Clear conversation history for this channel")
    async def clear_command(interaction: discord.Interaction):
        if bot.agent:
            bot.agent.clear_history(str(interaction.channel_id))
        await interaction.response.send_message("Conversation history cleared.")

    @bot.tree.command(name="help", description="Show available commands and usage guide")
    async def help_command(interaction: discord.Interaction):
        help_text = (
            "**Antigravity Controller - Help**\n\n"
            "**How to use:**\n"
            "- Mention me or send a DM with your request\n"
            "- I can read/write files, run commands, and manage git\n\n"
            "**Example messages:**\n"
            "- `Show me the project structure of /path/to/project`\n"
            "- `Read the file /path/to/file.py`\n"
            "- `What's the git status of /path/to/repo?`\n"
            "- `Run pytest in /path/to/project`\n"
            "- `Find all TODOs in /path/to/project`\n\n"
            "**Slash Commands:**\n"
            "- `/status` - Show bot configuration\n"
            "- `/clear` - Clear conversation history\n"
            "- `/help` - Show this help message\n\n"
            "**Security:**\n"
            "- I can only access files in allowed directories\n"
            "- Dangerous operations (write, execute, push) require your approval\n"
        )
        await interaction.response.send_message(help_text)
