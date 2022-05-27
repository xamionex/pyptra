import json
import discord
from discord.ext import commands, bridge
from cogs import utils, block
# afk command data
import time


def setup(bot):
    bot.add_cog(OtherCommands(bot))


class OtherCommands(commands.Cog, name="Other commands"):
    """Uncategorized commands with general use."""
    COG_EMOJI = "❔"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(hidden=True, name="echo")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def say(self, ctx, *, message=None):
        """Echoes the message you send."""
        await utils.delete_message(ctx)
        await ctx.send(message)

    @commands.command(hidden=True, name="echoembed")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def Say(self, ctx, *, message=None):
        """Echos the message you put in, was used for testing."""
        await utils.delete_message(ctx)
        embed = discord.Embed(color=ctx.author.color,
                              timestamp=ctx.message.created_at)
        embed.set_author(name="Announcement!", icon_url=ctx.author.avatar.url)
        embed.add_field(
            name=f"Sent by {ctx.message.author}", value=str(message))
        await ctx.send(embed=embed)

    @commands.command(hidden=True, name="reply")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reply(self, ctx, *, message=None):
        """Reply to someone's message with this command, It'll reply with the bot"""
        reference = ctx.message.reference
        if reference is None:
            return await ctx.reply(f"{ctx.author.mention} You didn't reply to any message.")
        await reference.resolved.reply(message)
        await utils.delete_message(ctx)

    @commands.command(hidden=True, name="namedm")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def namedm(self, ctx, user: discord.User, *, message=None):
        """DM someone with the message saying your name"""
        message = f"From {ctx.author.mention}: {message}" or f"{ctx.author.mention} sent you a message but it was empty"
        await user.send(message)
        await utils.delete_message(ctx)

    @commands.command(hidden=True, name="dm")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def dm(self, ctx, user: discord.User, *, message=None):
        """DM someone without the message saying your name"""
        message = message or "Someone sent you a message but it was empty"
        await user.send(message)
        await utils.delete_message(ctx)

    @commands.command(hidden=True, name="nick")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def nick(self, ctx, member: discord.Member, *, nick=None):
        """Changes a users nickname, mostly for testing purposes :)"""
        nick = nick or ""
        await member.edit(nick=nick)
        await utils.delete_message(ctx)

    @bridge.bridge_command(name="afk")
    async def afk(self, ctx, *, reason=None):
        """Alerts users that mention you that you're AFK."""
        if reason:
            reason = utils.remove_newlines(reason)
        e = await OtherUtils.setafk(self, ctx, reason)
        await OtherUtils.sendafk(self, ctx, ["afk_alert", "afk_alert_dm"], e)

    @bridge.bridge_command(name="gn")
    async def gn(self, ctx):
        """Sets your AFK to `Sleeping 💤`"""
        await OtherUtils.setafk(self, ctx, "Sleeping 💤")
        e = discord.Embed(description=f"Goodnight {ctx.author.mention}")
        e.set_image(url="https://c.tenor.com/nPYfVs6FsBQAAAAS/kitty-kitten.gif")
        await OtherUtils.sendafk(self, ctx, ["afk_alert", "afk_alert_dm"], e)


class OtherUtils():
    def __init__(self, ctx):
        self.ctx = ctx

    async def setafk(self, ctx, reason):
        with open('./data/afk.json', 'r') as f:
            afk = json.load(f)
        if not reason:
            reason = 'AFK'
        elif reason and len(reason) > 100:
            await utils.senderror(
                "You went over the 100 character limit")
        await OtherUtils.update_data(afk, ctx.author)
        afk[f'{ctx.author.id}']['reason'] = f'{reason}'
        if afk[f'{ctx.author.id}']['AFK']:
            rply = discord.Embed(
                description=f"Goodbye {ctx.author.mention}, Updated alert to \"{reason}\"")
        else:
            afk[f'{ctx.author.id}']['AFK'] = True
            afk[f'{ctx.author.id}']['time'] = int(time.time())
            afk[f'{ctx.author.id}']['mentions'] = 0
            rply = discord.Embed(
                description=f"Goodbye {ctx.author.mention}, Set alert to \"{reason}\"")
            try:
                await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
            except:
                pass
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)
        return rply

    async def update_data(afk, user):
        if not f'{user.id}' in afk:
            afk[f'{user.id}'] = {}
            afk[f'{user.id}']['AFK'] = False

    def period(delta, pattern):
        d = {'d': delta.days}
        d['h'], rem = divmod(delta.seconds, 3600)
        d['m'], d['s'] = divmod(rem, 60)
        return pattern.format(**d)

    async def sendafk(self, ctx, perm, e):
        if await block.GlobalBlockUtils.get_global_perm(self, ctx, perm[0], ctx.author):
            if await block.GlobalBlockUtils.get_global_perm(self, ctx, perm[1], ctx.author):
                await utils.senddmembed(ctx, e)
            else:
                if isinstance(ctx, bridge.BridgeApplicationContext):
                    await ctx.reply(embed=e, ephemeral=True)
                else:
                    await ctx.reply(embed=e, delete_after=10, mention_author=False)
