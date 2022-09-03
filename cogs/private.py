import discord
from discord.ext import commands
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(Private(bot))


class Private(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    async def priv(ctx):
        if ctx.author.id in [139095725110722560, 197344743301185536]:
            return True
        else:
            await Utils.send_error(ctx, f"Private commands are only allowed to certain users.")

    @commands.command(name="p", aliases=["pyramid", "pc"], hidden=True)
    @commands.check(priv)
    async def pyramid(self, ctx, num: int):
        r = 0
        for i in range(num):
            r += i + 1
        await ctx.respond(r)

    @commands.command(name="pl", aliases=["pyramidlist", "plist"], hidden=True)
    @commands.check(priv)
    async def pyramidlist(self, ctx, num: int):
        results = []
        r = 0
        for i in range(num):
            i += 1
            r += i
            results.append((i, r))
        e = discord.Embed(title="Result", description="")
        while len(results) > 21:
            results = results[1:]
        for r1, r2 in results:
            e.description += f"\n{r1} = {r2}"
        await ctx.respond(embed=e)

    @commands.command(name="calc", hidden=True)
    @commands.check(priv)
    async def calc(self, ctx, *, operation: str):
        await ctx.respond(eval(operation))
