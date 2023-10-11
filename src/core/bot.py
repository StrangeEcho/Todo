import logging
import os
from traceback import format_exception

import discord
from discord.ext import commands

from .confighandler import ConfigHandler


class TodoBot(commands.AutoShardedBot):
    discord.utils.setup_logging(level=logging.INFO)

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            help_command=None,
            intents=discord.Intents.all(),
        )
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config = ConfigHandler()
        self.todo_channel: int = self.config.get("todo_channel")
        self.owner_ids: set[int] = self.config.get("owner_ids")

    async def start(self) -> None:
        self.logger.info(f"Starting TodoBot(PID {os.getpid()})...")
        await self._load_extensions()
        await super().start(self.config.get("token"))

    async def on_ready(self) -> None:
        """Fired when discord dispatches that the bot is ready for use"""
        self.logger.info("TodoBot now ready...")

    async def on_error(self, event: str, *args, **kwargs) -> None:
        """General Error handler"""
        self.logger.exception(f"Unhandled exception in {event}.")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """General Error handler for commands framework"""
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandInvokeError):
            logging.getLogger(ctx.command.cog_name).error(
                "".join(format_exception(error))
            )
            await ctx.send(
                embed=discord.Embed(
                    title="Unhandled Exception Thrown",
                    description=f"```\n{error}\n```",
                    color=discord.Color.red(),
                ).set_footer(text="Check logs for full traceback")
            )
            return
        await ctx.send(
            embed=discord.Embed(description=error, color=discord.Color.red())
        )

    async def _load_extensions(self) -> None:
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
