import discord
from discord import app_commands
from discord.ext import commands

from core.bot import TodoBot


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
            emb.title = f"Task is being worked on by: {user}!"
            await msg.edit(embed=emb)
        if reaction.emoji == "✅":
            emb.color = discord.Color.green()
            emb.title="Task completed!"
            await msg.edit(embed=emb)

    @app_commands.command()
    @app_commands.describe(task="The task to be added to the todo list")
    async def todo(self, inter: discord.Interaction, *, task: str):
        """Add a task to the todo list"""
        await inter.response.defer()
        channel = self.bot.get_channel(self.bot.todo_channel)
        if not channel:
            return await inter.followup.send("No TODO channel set")
        msg = await channel.send(
            embed=discord.Embed(
                title="New Task!",
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

    @app_commands.command()
    @app_commands.describe(
        task_id = "The ID of the message the task is one",
        revision = "The revised task to replace the old one"
    )
    async def taskrevise(self, inter: discord.Interaction, task_id: str, *, revision: str):
        """Revise an open task"""
        await inter.response.defer()
        chan = inter.guild.get_channel(self.bot.todo_channel)
        task = await chan.fetch_message(int(task_id))
        if task.author.id != self.bot.user.id:
            return await inter.followup.send(f"Task ID invalid")
        emb = task.embeds[0]
        emb.description = revision
        await task.edit(embed=emb.set_footer(text="Task revised..."))
        await inter.followup.send(f"Finished revising task")

async def setup(bot: TodoBot) -> None:
    await bot.add_cog(Meta(bot))
