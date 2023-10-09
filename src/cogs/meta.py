from discord.ext import commands
from discord import app_commands
from core.todo import TodoBot

import discord

class Meta(commands.Cog):
    def __init__(self, bot: TodoBot):
        self.bot = bot
        self.reactions = {
            "👷",
            "✅"
        }
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        """Listen for the reactions and perform tasks accordingly"""
        msg = reaction.message
        if msg.guild.id != self.bot.todo_channel or msg.author.id != self.bot.user.id:
            return
        emb = msg.embeds[0]
        if reaction.emoji == "👷":
            emb.color = discord.Color.yellow()
            await msg.edit(
                embed=emb.set_footer(
                    icon_url=user.display_avatar.url,
                    text=f"Claimed by {user}"
                )
            )
        if reaction.emoji == "✅":
            emb.color = discord.Color.green()
            await msg.edit(
                embed=emb.set_footer(
                    icon_url=user.display_avatar.url,
                    text=f"Task Completed by {user}"
                )
            )
    
    @app_commands.command()
    @app_commands.describe(
        task="The task to be added to the todo list"
    )
    async def todo(self, inter: discord.Interaction, *, task: str):
        """Add a task to the todo list"""
        channel = self.bot.get_channel(self.bot.todo_channel)
        msg  = await channel.send(
            embed=discord.Embed(
                title="New Task",
                description=task,
                color=discord.Color.red()
            )
        )
        for reaction in self.reactions:
            await msg.add_reaction(reaction)
    
async def setup(bot: TodoBot):
    await bot.add_cog(Meta(bot))

        
    