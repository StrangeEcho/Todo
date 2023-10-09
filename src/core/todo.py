from discord.ext import commands
from discord import app_commands 

import discord

class TodoBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            help_command=None,
            intents=discord.Intents.all()
        )
        self.todo_channel: int = 123456 # The ID of the TODO channel 
        
    async def setup_hook(self):
        await self.tree.copy_global_to(guild=1158248328841146420)
        await self.tree.sync()
    
    async def start(self) -> None:
        await self.load_extension(f"cogs.main")
        await super().start("TOKEN")
    