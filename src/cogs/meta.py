import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
from core.bot import TodoBot
from typing import Literal

class TaskModal(Modal):
    def __init__(self, channel: int, *, modal_typle: Literal["Map", "Scripts"]):
        super().__init__(
            title="Map Task" if modal_typle == "Map" else "Scripting Task",
        )
        self.task_title = TextInput(
            label="Task Title",
            placeholder="The title of the task that you are proposing",
            style=discord.TextStyle.long
        )
        self.task_description = TextInput(
            label="Task Description",
            placeholder="Describe the tasks taht you want to propose",
            style=discord.TextStyle.long
        )
        self._todo_channel = channel 
        self._reactions = {"👷", "✅", "❌"}
        self.add_item(self.task_title)
        self.add_item(self.task_description)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chan = interaction.client.get_channel(self._todo_channel)
        msg = await chan.send(
            embed=discord.Embed(
                title=self.task_title.value,
                description=f"```\n{self.task_description.value}\n```",
                color=discord.Color.red(),
            )
            .set_author(
                name=f"Task proposed by: {interaction.user}",
                icon_url=interaction.user.display_avatar.url
            )
            .set_footer(
                text="❌ Decline | 👷 Claim | ✅ Mark Finished"
            )
        )
        for reaction in self._reactions:
            await msg.add_reaction(reaction)
        await interaction.followup.send(f"Finished adding task to Todolist", ephemeral=True)
        
        

class Meta(commands.Cog):
    def __init__(self, bot: TodoBot):
        self.bot = bot
        self.reactions: set[str] = {"👷", "✅", "❌"}

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
        if reaction.emoji == "❌":
            emb.title = "Task Rejected"
            await msg.edit(embed=emb.set_footer(text=f"Task rejected by {user}"))

    
    @commands.command(aliases=["latency"])
    async def ping(self, ctx: commands.Context):
        """Retrieves latency information on HTTP and WebSocket connection to Gateway"""
        msg = await ctx.send("Measuring now...")
        edit_latency = round(
            (msg.created_at - ctx.message.created_at).total_seconds() * 1000
        )
        await ctx.send(
            embed=discord.Embed(
                title="Measured Out Latency",
                color=discord.Color.blue()
            ).add_field(
                name="Websocket/Gateway",
                value="\n".join([f"`Shard ID: {shard_id} | {round(latency * 1000)}ms`" for shard_id, latency in self.bot.latencies])
            ).add_field(
                name="HTTP Protocol",
                value=f"`{edit_latency}ms`",
                inline=False
            )
        )
        await msg.delete()
    
    @commands.command() 
    async def cleanup(self, ctx: commands.Context, limit: int = 15):
        """Cleanup the bots messages"""
        msgs = await ctx.channel.purge(limit=limit, check=lambda x: x.author.id == self.bot.user.id)
        await ctx.send(f"Cleaned up {len(msgs)} of my messages", delete_after=5)

    @app_commands.command()
    @app_commands.describe(task_type="Pick between Map and Scripts")
    async def todo(self, inter: discord.Interaction, task_type: Literal["Map", "Scripts"]):
        """Add a task to the todo list"""
        await inter.response.send_modal(TaskModal(self.bot.todo_channel, modal_typle=task_type))
    

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
