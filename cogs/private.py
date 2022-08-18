import discord
from discord.ext import commands
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(Private(bot))


class Private(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    async def priv(ctx):
        users = [139095725110722560, 197344743301185536]
        users_str = [member.name for member in [ctx.bot.get_user(id) for id in users]]
        check = ctx.author.id in users
        if check:
            return True
        else:
            await Utils.send_error(ctx, f"Private commands are only allowed to these users: {', '.join(users_str)}")

    @commands.command(name="p", aliases=["pyramid", "pc"], hidden=True)
    @commands.check(priv)
    async def pyramid(self, ctx, num: int):
        num2 = 0
        while num > 0:
            num -= 1
            num2 += num + 1
        await ctx.respond(num2)

    @commands.command(name="pl", aliases=["pyramidlist", "plist"], hidden=True)
    @commands.check(priv)
    async def pyramidlist(self, ctx, num: int):
        results = []
        for i in range(num):
            i += 1
            i1, i2 = i, 0
            while i > 0:
                i2 += i
                i -= 1
            results.append((i1, i2))
        e = discord.Embed(title="Result", description="")
        while len(results) > 21:
            results = results[1:]
        for r1, r2 in results:
            e.description += f"\n{r1} = {r2}"
        await ctx.send(embed=e)

    @commands.command(name="calc", hidden=True)
    @commands.check(priv)
    async def calc(self, ctx, *, operation: str):
        await ctx.respond(eval(operation))
