import os
import sys
import discord
from discord.ext import commands
import utils

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
