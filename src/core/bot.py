from discord.ext import commands
from .confighandler import ConfigHandler

import discord
import os
import logging

class TodoBot(commands.AutoShardedBot):

    discord.utils.setup_logging(level=logging.INFO)

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            help_command=None,
            intents=discord.Intents.all()
        )
        self.logger = logging.getLogger(__name__)
        self.config = ConfigHandler()
        self.todo_channel: int = self.config.get("todo_channel")
        self.owner_ids: set[int] = self.config.get("owner_ids")
    
    async def start(self) -> None:
        self.logger.info(f"Starting TodoBot(PID {os.getpid()})...")
        await self._load_extensions()
        await super().start(self.config.get("token"))
    
    async def on_ready(self):
        """Fired when discord dispatches that the bot is ready for use"""
        self.logger.info("TodoBot now ready...")

    async def on_error(self, event: str, *args, **kwargs) -> None:
        """General Error handler"""
        self.logger.exception(f"Unhandled exception in {event}.")
    
    async def _load_extensions(self):
        """Helper to load all cogs/extension found in the cogs file"""
        self.logger.info("Attempting to load cog extensions")
        for ext in os.listdir("src/cogs"):
            if ext.endswith(".py"):
                cog = f"cogs.{ext[:-3]}"
                _logger = logging.getLogger(cog)
                try:
                    await self.load_extension(cog)
                    _logger.info("success...")
                except commands.ExtensionError as e:
                    _logger.error(f"failed...\n\n{e}")
    