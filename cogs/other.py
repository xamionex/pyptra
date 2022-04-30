import json
import discord
from discord.ext import commands, bridge
# afk command data
import datetime
import humanize
import time
# restart command
import sys
import os


class OtherCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx: discord.ApplicationContext):
        await ctx.message.delete()
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(name="echo")
    @commands.has_permissions(administrator=True)
    async def say(self, ctx, *, message=None):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="echoembed")
    @commands.has_permissions(administrator=True)
    async def Say(self, ctx, *, message=None):
        await ctx.message.delete()
        embed = discord.Embed(color=ctx.author.color,
                              timestamp=ctx.message.created_at)
        embed.set_author(name="Announcement!", icon_url=ctx.author.avatar.url)
        embed.add_field(
            name=f"Sent by {ctx.message.author}", value=str(message))
        await ctx.send(embed=embed)

    @commands.command(name="reply")
    @commands.has_permissions(administrator=True)
    async def reply(self, ctx, *, message=None):
        reference = ctx.message.reference
        if reference is None:
            return await ctx.reply(f"{ctx.author.mention} You didn't reply to any message")
        await reference.resolved.reply(message)
        await ctx.message.delete()

    @commands.command(name="namedm")
    @commands.has_permissions(administrator=True)
    async def namedm(self, ctx, user: discord.User, *, message=None):
        message = f"From {ctx.author.mention}: {message}" or f"{ctx.author.mention} sent you a message but it was empty"
        await user.send(message)
        await ctx.message.delete()

    @commands.command(name="dm")
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, user: discord.User, *, message=None):
        message = message or "Someone sent you a message but it was empty"
        await user.send(message)
        await ctx.message.delete()

    @commands.command(name="nick")
    @commands.has_permissions(administrator=True)
    async def nick(self, ctx, member: discord.Member, *, nick=None):
        nick = nick or "Cringe"
        await member.edit(nick=nick)
        await ctx.message.delete()

    @bridge.bridge_command(name="afk", description="Set an AFK so people know if you will respond after being pinged")
    async def afk(self, ctx, *, reason=None):
        e = await OtherUtils.setafk(self, ctx, reason)
        await ctx.respond(embed=e)

    @bridge.bridge_command(name="gn", description="Go to bed! >:C")
    async def gn(self, ctx):
        await OtherUtils.setafk(self, ctx, "Sleeping 💤")
        e = discord.Embed(description=f"Goodnight {ctx.author.mention}")
        e.set_image(url="https://c.tenor.com/nPYfVs6FsBQAAAAS/kitty-kitten.gif")
        await ctx.respond(embed=e)


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
        with open('./data/afk.json', 'r') as f:
            afk = json.load(f)
        for member in message.mentions:
            if member.bot:
                return
            if afk[f'{member.id}']['AFK'] == 'True':
                if message.author.bot:
                    return
                reason = afk[f'{member.id}']['reason']
                timeafk = int(time.time()) - int(afk[f'{member.id}']['time'])
                afktime = humanize.naturaltime(
                    datetime.datetime.now() - datetime.timedelta(seconds=timeafk))
                isafk = discord.Embed(
                    description=f"{member.mention} is afk: {reason} - {afktime}")
                await message.reply(embed=isafk, delete_after=10.0, mention_author=False)
                timementioned = int(afk[f'{member.id}']['mentions']) + 1
                afk[f'{member.id}']['mentions'] = timementioned
                with open('./data/afk.json', 'w') as f:
                    json.dump(afk, f, indent=4, sort_keys=True)
        if not message.author.bot:
            await OtherUtils.update_data(afk, message.author)
            if afk[f'{message.author.id}']['AFK'] == 'True':
                timeafk = int(time.time()) - \
                    int(afk[f'{message.author.id}']['time'])
                afktime = OtherUtils.period(datetime.timedelta(
                    seconds=round(timeafk)), "{d}d {h}h {m}m {s}s")
                mentionz = afk[f'{message.author.id}']['mentions']
                e = discord.Embed(
                    description=f"**Welcome back {message.author.mention}!**")
                e.add_field(name="Afk for", value=afktime, inline=True)
                e.add_field(name="Mentioned",
                            value=f"{mentionz} time(s)", inline=True)
                afk[f'{message.author.id}']['AFK'] = 'False'
                afk[f'{message.author.id}']['reason'] = 'None'
                afk[f'{message.author.id}']['time'] = '0'
                afk[f'{message.author.id}']['mentions'] = 0
                with open('./data/afk.json', 'w') as f:
                    json.dump(afk, f, indent=4, sort_keys=True)
                try:
                    nick = message.author.display_name.replace('[AFK]', '')
                    await message.author.edit(nick=nick)
                except:
                    print(
                        f'I wasnt able to edit [{message.author} / {message.author.id}].')
                await message.reply(embed=e, delete_after=10, mention_author=False)
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)

    def period(delta, pattern):
        d = {'d': delta.days}
        d['h'], rem = divmod(delta.seconds, 3600)
        d['m'], d['s'] = divmod(rem, 60)
        return pattern.format(**d)
