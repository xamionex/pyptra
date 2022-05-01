import json
import discord
from discord.ext import commands, bridge
from cogs import utils


class BlockUtils():
    async def get_member_data():
        with open("./data/perms.json") as f:
            users = json.load(f)
            return users

    async def open_member_perms(user):
        users = await BlockUtils.get_member_data()
        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["blacklist"] = False
            users[str(user.id)]["weird"] = False
            users[str(user.id)]["ping"] = False
            with open("./data/perms.json", "w") as f:
                json.dump(users, f, indent=4, sort_keys=True)
                return True

    async def get_blacklist(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        yn = users[str(user.id)]['blacklist']
        return yn

    async def get_weird(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        yn = users[str(user.id)]['weird']
        return yn

    async def get_ping(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        yn = users[str(user.id)]['ping']
        return yn

    async def add_blacklist(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['blacklist'] = True
        await BlockUtils.dump(users)

    async def remove_blacklist(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['blacklist'] = False
        await BlockUtils.dump(users)

    async def add_weird(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['weird'] = True
        await BlockUtils.dump(users)

    async def remove_weird(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['weird'] = False
        await BlockUtils.dump(users)

    async def add_ping(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['ping'] = True
        await BlockUtils.dump(users)

    async def remove_ping(user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)]['ping'] = False
        await BlockUtils.dump(users)

    async def dump(users):
        with open("./data/perms.json", "w") as f:
            json.dump(users, f, indent=4, sort_keys=True)


class BlockCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(name="block", description="Block a user to deny them from using the bot")
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx, user: discord.Member, *, reason=None):
        if await BlockUtils.get_blacklist(user) == True:
            await ctx.reply("The person is already blacklisted.")
        else:
            await BlockUtils.add_blacklist(user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has blacklisted {user.mention} for: {reason}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="unblock", description="Unblock a user to allow them to use the bot")
    @commands.has_permissions(administrator=True)
    async def unblacklist(self, ctx, user: discord.Member):
        if await BlockUtils.get_blacklist(user) == False:
            await ctx.reply("The person is already unblacklisted.")
        else:
            await BlockUtils.remove_blacklist(user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has unblacklisted {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="introvert", description="Don't let people use commands like pet on you")
    async def introvert(self, ctx):
        if await BlockUtils.get_ping(ctx.author) == True:
            await utils.senderror(ctx,
                                  f"I'm already not letting people use my commands with you.")
        else:
            await BlockUtils.add_ping(ctx.author)
            e = discord.Embed(
                description=f"I wont let people use my commands with you", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="extrovert", description="Let people use commands like pet on you")
    async def extrovert(self, ctx):
        if await BlockUtils.get_ping(ctx.author) == False:
            await utils.senderror(ctx,
                                  f"I'm already letting people use my commands with you.")
        else:
            await BlockUtils.remove_ping(ctx.author)
            e = discord.Embed(
                description=f"I'll let people use my commands with you", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="weird", description="Allow a user to use kiss, hug, pet, etc. commands")
    @commands.has_permissions(administrator=True)
    async def weird(self, ctx, user: discord.Member):
        if await BlockUtils.get_weird(user) == True:
            await utils.senderror(ctx, f"That person is already weird.")
        else:
            await BlockUtils.add_weird(user)
            e = discord.Embed(
                description=f"Made {user.mention} weird", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="unweird", description="Disallow a user to use kiss, hug, pet, etc. commands")
    @commands.has_permissions(administrator=True)
    async def unweird(self, ctx, user: discord.Member):
        if await BlockUtils.get_weird(user) == False:
            await utils.senderror(ctx, f"That person is already normal.")
        else:
            await BlockUtils.remove_weird(user)
            e = discord.Embed(
                description=f"Normalized {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)
