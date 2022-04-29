import json
import discord
from discord.ext import commands


class BlockUtils():
    async def open_member_perms(user):
        users = await BlockUtils.get_member_data()
        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["blacklist"] = False
            users[str(user.id)]["weird"] = False
            with open("./data/perms.json", "w") as f:
                json.dump(users, f, indent=4, sort_keys=True)
                return True

    async def get_blacklist(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        wallet_amt = users[str(user.id)]['blacklist']
        if wallet_amt == "True":
            return True
        else:
            return False

    async def get_weird(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        wallet_amt = users[str(user.id)]['weird']
        if wallet_amt == "True":
            return True
        else:
            return False

    async def get_member_data():
        with open("./data/perms.json") as f:
            users = json.load(f)
            return users

    async def add_blacklist(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['blacklist'] = True
        await BlockUtils.dump(users)

    async def add_weird(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['weird'] = True
        await BlockUtils.dump(users)

    async def remove_blacklist(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['blacklist'] = False
        await BlockUtils.dump(users)

    async def remove_weird(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['weird'] = False
        await BlockUtils.dump(users)

    async def dump(users):
        with open("./data/perms.json", "w") as f:
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
            blacklist = discord.Embed(
                description=f"{ctx.author.mention} has blacklisted {user.mention} for: {reason}", color=0xed4245)
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

    @commands.command(name="weird")
    @commands.has_permissions(administrator=True)
    async def weird(self, ctx, user: discord.Member):
        await ctx.message.delete()
        if await BlockUtils.get_weird(user) == 0:
            await BlockUtils.add_weird(user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has weirded {user.mention}", color=0xed4245)
            await ctx.send(embed=e)
        else:
            await ctx.send("The person is already weird.")

    @commands.command(name="unweird")
    @commands.has_permissions(administrator=True)
    async def unweird(self, ctx, user: discord.Member):
        await ctx.message.delete()
        if await BlockUtils.get_weird(user) != 0:
            await BlockUtils.remove_weird(user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has normalized {user.mention}", color=0x3ba55d)
            await ctx.send(embed=e)
        else:
            await ctx.send("The person is already normal.")
