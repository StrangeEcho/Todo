import typing
from typing import Any, List, Mapping, Optional

import discord
from discord.ext import commands
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import Command

from core.bot import TodoBot


class TodoHelpCommand(commands.HelpCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def send_bot_help(self, mapping: typing.Mapping):
        chan = self.get_destination()
        await chan.send(
            embed=discord.Embed(
                title=f":wave: Hello there. Im {self.context.bot.user.name}",
                description=f"{self.context.bot.user.name} is a task management bot created for the ModernRoleplay development/revival\n\n"
                "**Prefix**: "
                f"`!` or {self.context.bot.user.mention}\n\n"
                f"**Current Modules**:\n"
                + "\n".join(
                    [
                        f"`{cog.qualified_name}`"
                        for cog in self.context.bot.cogs.values()
                    ]
                ),
                color=discord.Color.blue(),
            )
            .set_thumbnail(url=self.context.bot.user.avatar.url)
            .set_footer(
                text=f"Do {self.context.clean_prefix}help <module/command> to for more info."
            ),
        )

    async def send_command_help(self, command: commands.Command) -> None:
        chan = self.get_destination()
        await chan.send(
            embed=discord.Embed(
                title=f"Info for `{command.qualified_name}`",
                description=f"Command Description: {'`{}`'.format(command.help) if command.help else '`No Description`'}",
                color=discord.Color.blue(),
            )
            .add_field(name="Module/Cog", value=f"`{command.cog_name}`")
            .add_field(
                name="Usage",
                value=f"`{self.context.clean_prefix}{command.qualified_name} {command.signature}`",
            )
            .add_field(
                name="Aliases",
                value=f"\n".join([f"`{a}`" for a in command.aliases])
                if command.aliases
                else "`None`",
            )
            .set_footer(
                text="<> params signify required arguments while [] signify optional arguments"
            )
        )

    async def send_cog_help(self, cog: commands.Cog) -> None:
        chan = self.get_destination()
        embed = discord.Embed(
            title=f"Info for `{cog.qualified_name.replace('_', ' ').title()}`",
            description=f"Description: {'`{}`'.format(cog.description) if cog.description else '`No Description`'}",
            color=discord.Color.blue(),
        )
        if cog.get_commands():
            embed.add_field(
                name="Commands",
                value="\n".join(
                    [
                        f"`{c.name}` `{c.aliases}`"
                        for c in await self.filter_commands(
                            cog.get_commands(), sort=True
                        )
                        if await c.can_run(self.context)
                    ]
                )
                or "`No Usable Commands.`",
            )
        embed.set_footer(
            text="Cog commands are filtered to the commands that are usable by you in the current context."
        )
        await chan.send(embed=embed)

    async def send_group_help(self, group: commands.Group) -> None:
        """Override method"""
        chan = self.get_destination()
        await chan.send(
            embed=discord.Embed(
                title=f"Info for Group command `{group.qualified_name}`",
                description=f"Description: {'`{}`'.format(group.help) if group.help else 'No Description'}",
                color=discord.Color.blue(),
            )
            .add_field(
                name="Subcommands",
                value="\n".join(
                    [
                        f"`{c.qualified_name}`"
                        for c in await self.filter_commands(group.commands, sort=True)
                        if await c.can_run(self.context)
                    ]
                ),
            )
            .set_footer(
                text=f"Use {self.context.clean_prefix}help <subcommand> for information on a command groups subcommand"
            )
        )

    async def command_not_found(self, string: str) -> discord.Embed:
        return discord.Embed(
            description=f"Couldn't find a Command/Group/Module[Cog] called `{string}`...",
            color=discord.Color.red(),
        ).set_footer(text=f"Run {self.context.clean_prefix}help for more info!")

    async def send_error_message(self, error) -> None:
        await self.get_destination().send(embed=error)


class Help(commands.Cog):
    def __init__(self, bot: TodoBot):
        self.bot = bot
        self.bot.help_command = TodoHelpCommand()


async def setup(bot: TodoBot):
    await bot.add_cog(Help(bot))
