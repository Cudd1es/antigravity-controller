"""Application entry point - starts the Discord Bot."""

import logging
import sys

from controller.bot.client import AntigravityBot
from controller.bot.commands import setup_commands
from controller.config import Config


def main():
    """Initialize configuration and start the Discord Bot."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    # Load config
    config = Config.from_env()
    errors = config.validate()
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        logger.error("Please check your .env file. See .env.example for reference.")
        sys.exit(1)

    # Create and configure bot
    bot = AntigravityBot(config)
    setup_commands(bot)

    # Run
    logger.info(f"Starting Antigravity Controller with model: {config.gemini_model}")
    logger.info(f"Allowed directories: {config.allowed_directories}")
    bot.run(config.discord_token, log_handler=None)


if __name__ == "__main__":
    main()
