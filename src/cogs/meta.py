from discord.ext import commands
from discord import app_commands
from core.bot import TodoBot

import discord


class Meta(commands.Cog):
    def __init__(self, bot: TodoBot):
        self.bot = bot
        self.reactions: set[str] = {"👷", "✅"}

    async def cog_load(self) -> None:
        self.bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(
        self, inter: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await inter.response.send_message(
            f"{inter.command.name} errored out.\n {error}"
        )

    @commands.Cog.listener()
    async def on_reaction_add(
        self, reaction: discord.Reaction, user: discord.Member
    ) -> None:
        """Listen for the reactions and perform tasks accordingly"""
        msg = reaction.message
        if user.bot or msg.channel.id != self.bot.todo_channel:
            return
        emb = msg.embeds[0]
        if reaction.emoji == "👷":
            emb.color = discord.Color.yellow()
            await msg.edit(
                embed=emb.set_footer(
                    icon_url=user.display_avatar.url, text=f"Claimed by {user}"
                )
            )
        if reaction.emoji == "✅":
            emb.color = discord.Color.green()
            await msg.edit(
                embed=emb.set_footer(
                    icon_url=user.display_avatar.url, text=f"Task Completed by {user}"
                )
            )

    @app_commands.command()
    @app_commands.describe(task="The task to be added to the todo list")
    async def todo(self, inter: discord.Interaction, *, task: str):
        """Add a task to the todo list"""
        await inter.response.defer()
        channel = self.bot.get_channel(self.bot.todo_channel)
        if not channel:
            return await inter.response.send_message("No TODO channel set")
        msg = await channel.send(
            embed=discord.Embed(
                title="New Task",
                description=f"```\n{task}\n```",
                color=discord.Color.red(),
            )
            .set_author(
                name=f"Task proposed by: {inter.user}",
            )
            .set_thumbnail(url=inter.user.display_avatar.url)
        )
        for reaction in self.reactions:
            await msg.add_reaction(reaction)
        await inter.followup.send(f"Finished adding task to Todolist", ephemeral=True)


async def setup(bot: TodoBot) -> None:
    await bot.add_cog(Meta(bot))
