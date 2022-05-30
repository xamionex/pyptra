import json
from typing import Optional
import discord
import os
import sys
from discord.ext import commands
from cogs import utils, configs

extensions = utils.extensions()


def setup(bot):
    bot.add_cog(ModerationCommands(bot))


class ModerationCommands(commands.Cog, name="Moderation"):
    """Moderation commands."""
    COG_EMOJI = "📛"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(hidden=True, name="purge")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, channel: Optional[discord.TextChannel], user: Optional[discord.Member], amount: int = None):
        """Purge a channel or user"""
        if amount:
            if channel and user:
                await channel.purge(limit=amount, check=lambda m: m.author == user)
            elif channel:
                await channel.purge(limit=amount)
            elif user:
                await ctx.channel.purge(limit=amount, check=lambda m: m.author == user)
            else:
                await ctx.channel.purge(limit=amount)
        else:
            await utils.senderror(ctx, "Specify amount of messages to delete")
