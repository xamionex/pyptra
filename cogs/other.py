import json
import discord
from discord.ext import commands, bridge
from cogs import utils, block
# afk command data
import datetime
import humanize
import time


def setup(bot):
    bot.add_cog(OtherCommands(bot))


class OtherCommands(commands.Cog, name="Other commands"):
    """Uncategorized commands with general use."""
    COG_EMOJI = "❔"

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx

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
        e = await OtherUtils.setafk(self, ctx, reason)
        if not ctx.author.bot and await block.BlockUtils.get_perm("afkcheck", ctx.author) == False:
            await utils.sendembed(ctx, e)

    @bridge.bridge_command(name="gn")
    async def gn(self, ctx):
        """Sets your AFK to `Sleeping 💤`"""
        await OtherUtils.setafk(self, ctx, "Sleeping 💤")
        e = discord.Embed(description=f"Goodnight {ctx.author.mention}")
        e.set_image(url="https://c.tenor.com/nPYfVs6FsBQAAAAS/kitty-kitten.gif")
        if not ctx.author.bot and await block.BlockUtils.get_perm("afkcheck", ctx.author) == False:
            await utils.sendembed(ctx, e)


class OtherUtils():
    async def setafk(self, ctx, reason):
        with open('./data/afk.json', 'r') as f:
            afk = json.load(f)
        if not reason:
            reason = 'AFK'
        elif reason and len(reason) > 100:
            raise commands.CommandError(
                "You went over the 100 character limit")
        await OtherUtils.update_data(afk, ctx.author)
        afk[f'{ctx.author.id}']['AFK'] = 'True'
        afk[f'{ctx.author.id}']['reason'] = f'{reason}'
        afk[f'{ctx.author.id}']['time'] = int(time.time())
        afk[f'{ctx.author.id}']['mentions'] = 0
        rply = discord.Embed(
            description=f"Goodbye {ctx.author.mention}, Your afk is \"{reason}\"")
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)
        try:
            await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
        except:
            print(f'I wasnt able to edit [{ctx.author} / {ctx.author.id}].')
        return rply

    async def update_data(afk, user):
        if not f'{user.id}' in afk:
            afk[f'{user.id}'] = {}
            afk[f'{user.id}']['AFK'] = 'False'

    async def afkjoin(member):
        print(f'{member} has joined the server!')
        with open('./data/afk.json', 'r') as f:
            afk = json.load(f)
        await OtherUtils.update_data(afk, member)
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)

    async def afkcheck(message):
        send = False
        afk_alert = discord.Embed(
            title=f"Members in your message are afk:")
        if message.author.bot:
            return
        with open('./data/afk.json', 'r') as f:
            afk = json.load(f)
        for member in message.mentions:
            if member.bot:
                return
            if afk[f'{member.id}']['AFK'] == 'True':
                send = True

                # gets afk message
                reason = afk[f'{member.id}']['reason']

                # gets unix time
                unix_time = int(time.time()) - int(afk[f'{member.id}']['time'])

                # user was afk for time.now() - time
                afktime = humanize.naturaltime(
                    datetime.datetime.now() - datetime.timedelta(seconds=unix_time))

                # add embed
                afk_alert.add_field(
                    name=f"{member.display_name.replace('[AFK]', '')} - {afktime}", value=f"\"{reason}\"", inline=True)

                # plus 1 time mentioned in afk.json
                afk[f'{member.id}']['mentions'] = int(
                    afk[f'{member.id}']['mentions']) + 1

                # save json
                with open('./data/afk.json', 'w') as f:
                    json.dump(afk, f, indent=4, sort_keys=True)

        if send:
            # if alerts are on
            if await block.BlockUtils.get_perm("afkcheck", message.author) == False:
                # send reply that mention is afk
                await message.reply(embed=afk_alert, delete_after=10.0, mention_author=False)
        await OtherUtils.update_data(afk, message.author)
        # if message's author is afk continue
        if afk[f'{message.author.id}']['AFK'] == 'True':
            # unix now - unix since afk
            timeafk = int(time.time()) - \
                int(afk[f'{message.author.id}']['time'])

            # make time readable for user
            afktime = OtherUtils.period(datetime.timedelta(
                seconds=round(timeafk)), "{d}d {h}h {m}m {s}s")

            # get mentions
            mentionz = afk[f'{message.author.id}']['mentions']

            # make embed
            welcome_back = discord.Embed(
                description=f"**Welcome back {message.author.mention}!**")
            welcome_back.add_field(name="Afk for", value=afktime, inline=True)
            welcome_back.add_field(
                name="Mentioned", value=f"{mentionz} time(s)", inline=True)

            # reset afk for user
            afk[f'{message.author.id}']['AFK'] = 'False'
            afk[f'{message.author.id}']['reason'] = 'None'
            afk[f'{message.author.id}']['time'] = '0'
            afk[f'{message.author.id}']['mentions'] = 0
            with open('./data/afk.json', 'w') as f:
                json.dump(afk, f, indent=4, sort_keys=True)

            # try to reset nickname
            try:
                nick = message.author.display_name.replace('[AFK]', '')
                await message.author.edit(nick=nick)
            except:
                print(
                    f'I wasnt able to edit [{message.author} / {message.author.id}].')

            await message.reply(embed=welcome_back, delete_after=10, mention_author=False)
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)

    def period(delta, pattern):
        d = {'d': delta.days}
        d['h'], rem = divmod(delta.seconds, 3600)
        d['m'], d['s'] = divmod(rem, 60)
        return pattern.format(**d)
