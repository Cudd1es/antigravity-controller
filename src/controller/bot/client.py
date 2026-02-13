"""Discord Bot client with message handling and confirmation system."""

import asyncio
import logging

import discord
from discord.ext import commands

from controller.agent.core import Agent
from controller.bot.formatter import format_error, split_message
from controller.config import Config
from controller.security.permissions import PermissionManager
from controller.tools.base import ToolRegistry
from controller.tools.file_tools import (
    ListDirectoryTool,
    ReadFileTool,
    SearchInFilesTool,
    WriteFileTool,
)
from controller.tools.git_tools import (
    GitCommitTool,
    GitDiffTool,
    GitLogTool,
    GitPushTool,
    GitStatusTool,
)
from controller.tools.project_tools import FileInfoTool, FindTodosTool, ProjectStructureTool
from controller.tools.shell_tools import RunCommandTool

logger = logging.getLogger(__name__)


class ConfirmationView(discord.ui.View):
    """Discord UI View with Approve/Deny buttons for dangerous operations."""

    def __init__(self, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.result: bool | None = None
        self._event = asyncio.Event()

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji=None)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = True
        self._event.set()
        await interaction.response.edit_message(
            content=interaction.message.content + "\n**Approved**",
            view=None,
        )

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji=None)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = False
        self._event.set()
        await interaction.response.edit_message(
            content=interaction.message.content + "\n**Denied**",
            view=None,
        )

    async def on_timeout(self):
        self.result = False
        self._event.set()

    async def wait_for_result(self) -> bool:
        """Wait for user to click a button or timeout."""
        await self._event.wait()
        return self.result or False


class AntigravityBot(commands.Bot):
    """Discord Bot that integrates Gemini AI with local development tools."""

    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.config = config
        self.agent: Agent | None = None
        self.permissions: PermissionManager | None = None

    async def setup_hook(self):
        """Initialize agent, tools, and permissions on bot startup."""
        # Build tool registry
        registry = ToolRegistry()
        registry.register(ReadFileTool())
        registry.register(WriteFileTool())
        registry.register(ListDirectoryTool())
        registry.register(SearchInFilesTool())
        registry.register(GitStatusTool())
        registry.register(GitDiffTool())
        registry.register(GitLogTool())
        registry.register(GitCommitTool())
        registry.register(GitPushTool())
        registry.register(RunCommandTool(timeout=self.config.command_timeout_seconds))
        registry.register(ProjectStructureTool())
        registry.register(FileInfoTool())
        registry.register(FindTodosTool())

        # Build permission manager
        self.permissions = PermissionManager(self.config)

        # Build agent
        self.agent = Agent(self.config, registry, self.permissions)

        logger.info("Antigravity Bot initialized, waiting for connection...")

    async def on_ready(self):
        """Called when the bot is connected and ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Allowed directories: {self.config.allowed_directories}")
        logger.info(f"Gemini model: {self.config.gemini_model}")

        # Sync slash commands after bot is fully connected
        try:
            if self.config.discord_guild_id:
                guild = discord.Object(id=int(self.config.discord_guild_id))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info(f"Synced slash commands to guild {self.config.discord_guild_id}")
            else:
                await self.tree.sync()
                logger.info("Synced slash commands globally")
        except discord.errors.Forbidden:
            logger.warning(
                "Could not sync slash commands (Missing Access). "
                "Make sure the bot is invited with 'applications.commands' scope. "
                "Basic message handling will still work."
            )
        except Exception as e:
            logger.warning(f"Slash command sync failed: {e}. Message handling still works.")

        logger.info("Antigravity Bot is ready!")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore bot's own messages
        if message.author == self.user:
            return

        # Ignore messages from other bots
        if message.author.bot:
            return

        # Check if bot is mentioned or message is in DM
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = self.user in message.mentions if self.user else False

        # Only respond to DMs or mentions
        if not is_dm and not is_mentioned:
            # Process slash commands
            await self.process_commands(message)
            return

        # Check user permissions
        if not self.permissions.is_user_allowed(message.author.id):
            await message.reply(format_error("You are not authorized to use this bot."))
            return

        # Clean the message (remove bot mention)
        content = message.content
        if self.user:
            content = content.replace(f"<@{self.user.id}>", "").strip()
            content = content.replace(f"<@!{self.user.id}>", "").strip()

        if not content:
            await message.reply("Please provide a message.")
            return

        # Show typing indicator while processing
        async with message.channel.typing():
            # Create confirmation callback for this channel
            async def confirm_callback(tool_name: str, description: str) -> bool:
                confirm_msg = f"**Confirmation required for dangerous operation:**\n{description}"
                view = ConfirmationView(timeout=60.0)
                await message.channel.send(confirm_msg, view=view)
                return await view.wait_for_result()

            # Process through AI agent
            response = await self.agent.process_message(
                channel_id=str(message.channel.id),
                user_message=content,
                confirmation_callback=confirm_callback,
            )

        # Send response (split if needed)
        chunks = split_message(response)
        for chunk in chunks:
            await message.channel.send(chunk)
