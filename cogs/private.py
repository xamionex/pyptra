import discord
from discord.ext import bridge, commands


def setup(bot):
    bot.add_cog(Private(bot))


MISSING: object() = discord.utils.MISSING


class Private(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    def priv(ctx):
        return ctx.author.id in [139095725110722560, 197344743301185536]

    @commands.command(name="pyramid", hidden=True)
    @commands.check(priv)
    async def calc(self, ctx, num: int):
        num2 = 0
        while num > 0:
            num -= 1
            num2 += num + 1
        await ctx.respond(num2)

    @commands.command(name="calc", hidden=True)
    @commands.check(priv)
    async def calc(self, ctx, *, operation: str):
        await ctx.respond(eval(operation))
