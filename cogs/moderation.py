import re
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
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, channel: Optional[discord.TextChannel], user: Optional[discord.Member], amount: int):
        """Purge a channel or user"""
        await Utils.delete_command_message(ctx)
        if channel and user:
            await channel.purge(limit=amount, check=lambda m: m.author == user and not m.pinned)
        elif channel:
            await channel.purge(limit=amount, check=lambda m: not m.pinned)
        elif user:
            await ctx.channel.purge(limit=amount, check=lambda m: m.author == user and not m.pinned)
        else:
            await ctx.channel.purge(limit=amount, check=lambda m: not m.pinned)

    @commands.group(hidden=True, name="timedpurge", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def timed_purge(self, ctx):
        """Purge a channel in intervals"""
        await Utils.send_error(ctx, f"No command specified, do {self.ctx.settings[str(ctx.guild.id)]['prefix']}help timedpurge for more info")

    @timed_purge.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def add_purge(self, ctx, channel: Optional[discord.TextChannel], interval: int):
        """Add a purge to a channel that happens in intervals"""
        interval = int(''.join(re.findall('\d+', str(interval))))
        if interval <= 9:
            await Utils.send_error(ctx, "Minimum interval is 10 seconds.")
        settings = self.ctx.settings[str(ctx.guild.id)]["purges"]
        try:
            settings[str(channel.id)] = [interval, 0]
        except KeyError:
            settings = {}
            settings[str(channel.id)] = [interval, 0]
        await Utils.send_embed(ctx, discord.Embed(description=f"Added {channel.mention} to timed purges"), False)
        configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    @timed_purge.command(name="rem")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def rem_purge(self, ctx, channel: Optional[discord.TextChannel]):
        """Remove a purge from a channel"""
        settings = self.ctx.settings[str(ctx.guild.id)]["purges"]
        if str(channel.id) in settings:
            settings.pop(str(channel.id))
            await Utils.send_embed(ctx, discord.Embed(description=f"Removed {channel.mention} from timed purges"), False)
        else:
            await Utils.send_error(ctx, "That channel doesn't have a timed purge")
        configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    @timed_purge.command(name="reset")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def reset_purge(self, ctx, channel: Optional[discord.TextChannel]):
        """Reset a purge in a channel"""
        settings = self.ctx.settings[str(ctx.guild.id)]["purges"]
        if str(channel.id) in settings:
            settings[(str(channel.id))][1] = Utils.current_time() + settings[(str(channel.id))][0]
            await Utils.send_embed(ctx, discord.Embed(description=f"Reset {channel.mention}'s timed purge, it will happen in <t:{Utils.current_time() + settings[(str(channel.id))][0]}:R>"), False)
        else:
            await Utils.send_error(ctx, "That channel doesn't have a timed purge")
        configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    @timed_purge.command(name="list")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def list_purges(self, ctx):
        """List all timed purges"""
        if self.ctx.settings[str(ctx.guild.id)]["purges"]:
            e = discord.Embed(title="Listing all timed purges:")
            for channel, timed in self.ctx.settings[str(ctx.guild.id)]["purges"].items():
                try:
                    channel = f"{channel}\n{self.ctx.get_channel(int(channel)).name}"
                except:
                    channel = f"{channel}\nCouldn't get name"
                counter = Utils.display_time_s(timed[0])
                e.add_field(name=channel, value=f"Occurs every\n{counter}")
            await Utils.send_embed(ctx, e, False)
        else:
            await Utils.send_error(ctx, "This guild doesn't have timed purges")
