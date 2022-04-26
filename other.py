import datetime
import dbm
import json
import os
import sys
import time
import humanize
import discord
from discord.ext import commands
import utils


gn_options = [
    discord.OptionChoice(name="Goodnight", value="1"),
    discord.OptionChoice(name="I hope no-one looks at my plans", value="2")
]

class OtherCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx
        utils.ctx = ctx

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
        embed = discord.Embed(color=ctx.author.color,timestamp=ctx.message.created_at)
        embed.set_author(name="Announcement!", icon_url=ctx.author.avatar.url)
        embed.add_field(name=f"Sent by {ctx.message.author}", value=str(message))
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

    @commands.command(name="afk")
    async def afk1(self, ctx, *, reason=None):
        rply = await OtherUtils.afk(self, ctx, reason)
        await ctx.message.add_reaction('👋')
        await ctx.reply(rply, delete_after=10.0, mention_author=False)

    @commands.slash_command(name="afk")
    async def afk2(self, ctx, reason: discord.Option(str, "What do you want to set your AFK to?")):
        rply = await OtherUtils.afk(self, ctx, reason)
        await ctx.respond(rply, ephemeral=True)

    @commands.command(name="gn")
    async def gn1(self, ctx, *, option=None):
        if option == "2":
            await ctx.message.add_reaction('😈')
        else:
            await ctx.message.add_reaction('💤')
        rply = await OtherUtils.gn(self, ctx, option)
        await ctx.reply(rply, delete_after=10.0, mention_author=False)

    @commands.slash_command(name="gn")
    async def gn2(self, ctx, option: discord.Option(str, "What do you want to set your AFK to?", choices=gn_options)):
        rply = await OtherUtils.gn(self, ctx, option)
        await ctx.respond(rply, ephemeral=True)

class OtherUtils():
    async def gn(self, ctx, option):
        rply = await OtherUtils.afk(self, ctx, "Sleeping 💤")
        if option == "2":
            rply = await OtherUtils.afk(self, ctx, "https://cdn.discordapp.com/attachments/920776187884732559/961666631073947709/I_hope_no_one_looks_at_my_plans.mp4")
        return rply

    async def afk(self, ctx, reason):
        with open('./src/afk.json', 'r') as f:
            afk = json.load(f)
        if not reason:
            reason = 'AFK'
        await OtherUtils.update_data(afk, ctx.author)
        afk[f'{ctx.author.id}']['AFK'] = 'True'
        afk[f'{ctx.author.id}']['reason'] = f'{reason}'
        afk[f'{ctx.author.id}']['time'] = int(time.time())
        afk[f'{ctx.author.id}']['mentions'] = 0
        rply = f"I've set your AFK to \"{reason}\""
        with open('./src/afk.json', 'w') as f:
            json.dump(afk, f)
        try:
            await ctx.author.edit(nick=f'[AFK]{ctx.author.display_name}')
        except:
            print(f'I wasnt able to edit [{ctx.author} / {ctx.author.id}].')
        return rply

    async def update_data(afk, user):
        if not f'{user.id}' in afk:
            afk[f'{user.id}'] = {}
            afk[f'{user.id}']['AFK'] = 'False'

    async def afkjoin(member):
        print(f'{member} has joined the server!')
        with open('./src/afk.json', 'r') as f:
            afk = json.load(f)
        await OtherUtils.update_data(afk, member)
        with open('./src/afk.json', 'w') as f:
            json.dump(afk, f)

    async def afkcheck(message):
        with open('./src/afk.json', 'r') as f:
            afk = json.load(f)
        for member in message.mentions:
            if afk[f'{member.id}']['AFK'] == 'True':
                if message.author.bot:
                    return
                reason = afk[f'{member.id}']['reason']
                timeafk = int(time.time()) - int(afk[f'{member.id}']['time'])
                afktime = humanize.naturaltime(datetime.datetime.now() - datetime.timedelta(seconds=timeafk))
                await message.reply(f"{member.display_name} is afk: {reason} - {afktime}", delete_after=10.0, mention_author=False)
                timementioned = int(afk[f'{member.id}']['mentions']) + 1
                afk[f'{member.id}']['mentions'] = timementioned
                with open('./src/afk.json', 'w') as f:
                    json.dump(afk, f)
        if not message.author.bot:
            await OtherUtils.update_data(afk, message.author)
            if afk[f'{message.author.id}']['AFK'] == 'True':
                timeafk = int(time.time()) - int(afk[f'{message.author.id}']['time'])
                afktime = OtherUtils.period(datetime.timedelta(seconds=round(timeafk)), "{d}d {h}h {m}m {s}s")
                mentionz = afk[f'{message.author.id}']['mentions']
                await message.reply(f"Welcome back {message.author.display_name}!\nYou've been afk for {afktime}\nYou got mentioned {mentionz} times", delete_after=10.0, mention_author=False)
                afk[f'{message.author.id}']['AFK'] = 'False'
                afk[f'{message.author.id}']['reason'] = 'None'
                afk[f'{message.author.id}']['time'] = '0'
                afk[f'{message.author.id}']['mentions'] = 0
                with open('./src/afk.json', 'w') as f:
                    json.dump(afk, f)
                try:
                    await message.author.edit(nick=f'{message.author.display_name[5:]}')
                except:
                    print(f'I wasnt able to edit [{message.author} / {message.author.id}].')
        with open('./src/afk.json', 'w') as f:
            json.dump(afk, f)

    def period(delta, pattern):
        d = {'d': delta.days}
        d['h'], rem = divmod(delta.seconds, 3600)
        d['m'], d['s'] = divmod(rem, 60)
        return pattern.format(**d)