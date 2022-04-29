import datetime
import json
import os
import sys
import time
import humanize
import discord
from discord.ext import commands


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

    @commands.command(name="dm")
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, user: discord.User, *, message=None):
        message = f"From {ctx.author.mention}: {message}" or f"{ctx.author.mention} sent you a message but it was empty"
        await user.send(message)
        await ctx.message.delete()

    @commands.command(name="anondm")
    @commands.has_permissions(administrator=True)
    async def anondm(self, ctx, user: discord.User, *, message=None):
        message = message or "Someone sent you a message but it was empty"
        await user.send(message)
        await ctx.message.delete()

    @commands.command(name="nick")
    @commands.has_permissions(administrator=True)
    async def nick(self, ctx, member: discord.Member, *, nick=None):
        nick = nick or "Cringe"
        await member.edit(nick=nick)
        await ctx.message.delete()

    @commands.command(name="afk", description="Set an AFK so people know if you will respond after being pinged")
    async def afk1(self, ctx, *, reason=None):
        rply = await OtherUtils.afk(self, ctx, reason)
        await ctx.message.add_reaction('👋')
        await ctx.reply(embed=rply, delete_after=10.0, mention_author=False)

    @commands.slash_command(name="afk", description="Set an AFK so people know if you will respond after being pinged")
    async def afk2(self, ctx, reason: discord.Option(str, "What do you want to set your AFK to?")):
        rply = await OtherUtils.afk(self, ctx, reason)
        await ctx.respond(embed=rply, ephemeral=True)

    @commands.command(name="gn", description="Go to bed! >:C")
    async def gn1(self, ctx):
        await ctx.message.add_reaction('💤')
        e = await OtherUtils.gn(self, ctx, "Sleeping 💤")
        await ctx.reply(embed=e, delete_after=10.0, mention_author=False)

    @commands.slash_command(name="gn", description="Go to bed! >:C")
    async def gn2(self, ctx):
        e = await OtherUtils.gn(self, ctx, "Sleeping 💤")
        await ctx.respond(embed=e, ephemeral=True)


class OtherUtils():
    async def afk(self, ctx, reason):
        with open('./data/afk.json', 'r') as f:
            afk = json.load(f)
        if not reason:
            reason = 'AFK'
        await OtherUtils.update_data(afk, ctx.author)
        afk[f'{ctx.author.id}']['AFK'] = 'True'
        afk[f'{ctx.author.id}']['reason'] = f'{reason}'
        afk[f'{ctx.author.id}']['time'] = int(time.time())
        afk[f'{ctx.author.id}']['mentions'] = 0
        rply = discord.Embed(description=f"I've set your AFK to \"{reason}\"")
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)
        try:
            await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
        except:
            print(f'I wasnt able to edit [{ctx.author} / {ctx.author.id}].')
        return rply

    async def gn(self, ctx, reason):
        await OtherUtils.afk(self, ctx, reason)
        e = discord.Embed(description=f"Goodnight {ctx.author.display_name}")
        e.set_image(url="https://c.tenor.com/nPYfVs6FsBQAAAAS/kitty-kitten.gif")
        return e

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
                    description=f"{member.display_name} is afk: {reason} - {afktime}")
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
                back = discord.Embed(
                    title=f"Welcome back {message.author.display_name}!")
                back.add_field(name="Afk for", value=afktime, inline=True)
                back.add_field(name="Mentioned",
                               value=f"{mentionz} time(s)", inline=True)
                await message.reply(embed=back, delete_after=10.0, mention_author=False)
                afk[f'{message.author.id}']['AFK'] = 'False'
                afk[f'{message.author.id}']['reason'] = 'None'
                afk[f'{message.author.id}']['time'] = '0'
                afk[f'{message.author.id}']['mentions'] = 0
                with open('./data/afk.json', 'w') as f:
                    json.dump(afk, f, indent=4, sort_keys=True)
                try:
                    await message.author.edit(nick=f'{message.author.display_name[6:]}')
                except:
                    print(
                        f'I wasnt able to edit [{message.author} / {message.author.id}].')
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)

    def period(delta, pattern):
        d = {'d': delta.days}
        d['h'], rem = divmod(delta.seconds, 3600)
        d['m'], d['s'] = divmod(rem, 60)
        return pattern.format(**d)
