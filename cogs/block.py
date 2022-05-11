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
            await BlockUtils.set_member_perms(users, user)

    async def set_member_perms(users, user):
        users[str(user.id)] = {}
        perm_list = {'blacklist', "weird", "ping"}
        for value in perm_list:
            users[str(user.id)][value] = False
        with open("./data/perms.json", "w") as f:
            json.dump(users, f, indent=4, sort_keys=True)
            return True

    async def get_perm(perm, user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        yn = users[str(user.id)][perm]
        return yn

    async def add_perm(perm, user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)][perm] = True
        await BlockUtils.dump(users)

    async def remove_perm(perm, user):
        await BlockUtils.open_member_perms(user)
        users = await BlockUtils.get_member_data()
        users[str(user.id)][perm] = False
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
        if await BlockUtils.get_perm("blacklist", user) == True:
            await ctx.reply("The person is already blacklisted.")
        else:
            await BlockUtils.add_perm("blacklist", user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has blacklisted {user.mention} for: {reason}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="unblock", description="Unblock a user to allow them to use the bot")
    @commands.has_permissions(administrator=True)
    async def unblacklist(self, ctx, user: discord.Member):
        if await BlockUtils.get_perm("blacklist", user) == False:
            await ctx.reply("The person is already unblacklisted.")
        else:
            await BlockUtils.remove_perm("blacklist", user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has unblacklisted {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="introvert", description="Don't let people use commands like pet on you")
    async def introvert(self, ctx):
        if await BlockUtils.get_perm("ping", ctx.author) == True:
            await utils.senderror(ctx,
                                  f"I'm already not letting people use my commands with you.")
        else:
            await BlockUtils.add_perm("ping", ctx.author)
            e = discord.Embed(
                description=f"I wont let people use my commands with you", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="extrovert", description="Let people use commands like pet on you")
    async def extrovert(self, ctx):
        if await BlockUtils.get_perm("ping", ctx.author) == False:
            await utils.senderror(ctx,
                                  f"I'm already letting people use my commands with you.")
        else:
            await BlockUtils.remove_perm("ping", ctx.author)
            e = discord.Embed(
                description=f"I'll let people use my commands with you", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="weird", description="Allow a user to use kiss, hug, pet, etc. commands")
    @commands.has_permissions(administrator=True)
    async def weird(self, ctx, user: discord.Member):
        if await BlockUtils.get_perm("weird", user) == True:
            await utils.senderror(ctx, f"That person is already weird.")
        else:
            await BlockUtils.add_perm("weird", user)
            e = discord.Embed(
                description=f"Made {user.mention} weird", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="unweird", description="Disallow a user to use kiss, hug, pet, etc. commands")
    @commands.has_permissions(administrator=True)
    async def unweird(self, ctx, user: discord.Member):
        if await BlockUtils.get_perm("weird", user) == False:
            await utils.senderror(ctx, f"That person is already normal.")
        else:
            await BlockUtils.remove_perm("weird", user)
            e = discord.Embed(
                description=f"Normalized {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="reset", description="Reset a user's permissions in the bot")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx, user: discord.Member):
        users = await BlockUtils.get_member_data()
        if str(user.id) in users:
            users.pop(str(user.id))
            yn = await BlockUtils.set_member_perms(users, user)
            if yn:
                await utils.sendembed(ctx, e=discord.Embed(description=f"Successfully reset {user.mention}'s perms", color=0x66FF99))
            else:
                await utils.senderror(ctx, f"Couldn't reset {user.mention}")
        else:
            await utils.senderror(ctx, "User isn't in data")
