from typing import Optional
import discord
from discord.ext import commands
from cogs import configs
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(ModerationCommands(bot))


class ModerationCommands(commands.Cog, name="Moderation"):
    """Moderation commands."""
    COG_EMOJI = "📛"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(hidden=True, name="purge")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, channel: Optional[discord.TextChannel], user: Optional[discord.Member], amount: int = None):
        """Purge a channel or user"""
        await Utils.delete_command_message(ctx)
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
            await Utils.send_error(ctx, "Specify amount of messages to delete")

    @commands.group(hidden=True, name="timedpurge", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def timed_purge(self, ctx):
        """Purge a channel in intervals"""
        await Utils.send_error(ctx, f"No command specified, do {self.ctx.guild_prefixes[str(ctx.guild.id)]}help timedpurge for more info")

    @timed_purge.command(name="add")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def add_purge(self, ctx, channel: Optional[discord.TextChannel], interval: int = None):
        """Add a purge to a channel that happens in intervals"""
        timed_purge = self.ctx.timed_purge
        try:
            timed_purge[str(ctx.guild.id)][str(channel.id)] = [interval, 0]
        except KeyError:
            timed_purge[str(ctx.guild.id)] = {}
            timed_purge[str(ctx.guild.id)][str(channel.id)] = [interval, 0]
        await Utils.send_embed(ctx, discord.Embed(description=f"Added {channel.mention} to timed purges"), False)
        configs.save(self.ctx.timed_purge_path, "w", timed_purge)

    @timed_purge.command(name="rem")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def rem_purge(self, ctx, channel: Optional[discord.TextChannel]):
        """Remove a purge from a channel"""
        timed_purge = self.ctx.timed_purge
        try:
            timed_purge[str(ctx.guild.id)].pop(str(channel.id))
            await Utils.send_embed(ctx, discord.Embed(description=f"Removed {channel.mention} from timed purges"), False)
        except:
            await Utils.send_error(ctx, "That channel doesn't have a timed purge")
        configs.save(self.ctx.timed_purge_path, "w", timed_purge)

    @timed_purge.command(name="list")
    async def list_purges(self, ctx):
        """List all timed purges"""
        if self.ctx.timed_purge[str(ctx.guild.id)]:
            e = discord.Embed(title="Listing all timed purges:")
            for channel, timed in self.ctx.timed_purge[str(ctx.guild.id)].items():
                try:
                    channel = f"{channel}\n{self.ctx.get_channel(int(channel)).name}"
                except:
                    channel = f"{channel}\nCouldn't get name"
                counter = Utils.display_time_s(timed[0])
                e.add_field(
                    name=channel, value=f"Occurs every\n{counter}")
            await Utils.send_embed(ctx, e, False)
        else:
            await Utils.send_error(ctx, "This guild doesn't have timed purges")
