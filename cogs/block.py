import json
import discord
from discord.ext import commands

class BlockUtils():
    async def open_blacklisted(user):
        users = await BlockUtils.get_blacklisted_data()
        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["blacklist"] = 0
            with open("./data/blacklisted.json", "w") as f:
                json.dump(users, f, indent=4, sort_keys=True)
                return True

    async def get_blacklist(user):
        await BlockUtils.open_blacklisted(user)
        users = await BlockUtils.get_blacklisted_data()
        wallet_amt = users[str(user.id)]['blacklist']
        return wallet_amt

    async def get_blacklisted_data():
        with open("./data/blacklisted.json") as f:
            users = json.load(f)
            return users

    async def add_blacklist(user):
        await BlockUtils.open_blacklisted(user)
        users = await BlockUtils.get_blacklisted_data()
        users[str(user.id)]['blacklist'] += 1
        with open("./data/blacklisted.json", "w") as f:
            json.dump(users, f, indent=4, sort_keys=True)

    async def remove_blacklist(user):
        await BlockUtils.open_blacklisted(user)
        users = await BlockUtils.get_blacklisted_data()
        users[str(user.id)]['blacklist'] -= 1
        with open("./data/blacklisted.json", "w") as f:
            json.dump(users, f, indent=4, sort_keys=True)

class BlockCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(name="block")
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx, user: discord.Member, *, reason=None):
        await ctx.message.delete()
        if await BlockUtils.get_blacklist(user) == 0:
            await BlockUtils.add_blacklist(user)
            blacklist = discord.Embed(description=f"{ctx.author.mention} has blacklisted {user.mention} for: {reason}", color=0xed4245)
            await ctx.send(embed=blacklist)
        else:
            await ctx.send("The person is already blacklisted.")

    @commands.command(name="unblock")
    @commands.has_permissions(administrator=True)
    async def unblacklist(self, ctx, user: discord.Member):
        await ctx.message.delete()
        if await BlockUtils.get_blacklist(user) != 0:
            await BlockUtils.remove_blacklist(user)
            unblacklist = discord.Embed(
                description=f"{ctx.author.mention} has unblacklisted {user.mention}", color=0x3ba55d)
            await ctx.send(embed=unblacklist)
        else:
            await ctx.send("The person is already unblacklisted.")
