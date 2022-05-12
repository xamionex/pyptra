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

    def get_perms_list():
        perms = {"blacklist": "Denies usage for bot",
                 "weird": "Allows -hug -kiss",
                 "ping": "Denies pinging user in -hug -kiss -pet",
                 "pet": "Allows petting users/images/emojis",
                 "joke": "Allows using -fall -promote",
                 "afkcheck": "Denies/Allows AFK alerts"}
        return perms

    async def set_member_perms(users, user):
        users[str(user.id)] = {}
        perms = BlockUtils.get_perms_list()
        for value in perms:
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

    async def check_perm_arg(self, ctx):
        perms_list = BlockUtils.get_perms_list()
        for perms, perm_desc in perms_list:
            msg = ctx.message.content.split(" ")[2]
            if msg in perms:
                return msg
            else:
                await utils.senderror(ctx, f"{ctx.author.mention}, I couldn't find that permission.")


class BlockCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(name="block", description="Block a user to deny them from using the bot")
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx, user: discord.Member, *, reason=None):
        if await BlockUtils.get_blacklist(user) == True:
            if await BlockUtils.get_perm("blacklist", user) == True:
                await ctx.reply("The person is already blacklisted.")
            else:
                await BlockUtils.add_blacklist(user)
                await BlockUtils.add_perm("blacklist", user)
                e = discord.Embed(
                    description=f"{ctx.author.mention} has blacklisted {user.mention} for: {reason}", color=0xFF6969)
                await utils.sendembed(ctx, e, False)

    @commands.command(name="unblock", description="Unblock a user to allow them to use the bot")
    @commands.has_permissions(administrator=True)
    async def unblacklist(self, ctx, user: discord.Member):
        if await BlockUtils.get_blacklist(user) == False:
            if await BlockUtils.get_perm("blacklist", user) == False:
                await ctx.reply("The person is already unblacklisted.")
            else:
                await BlockUtils.remove_blacklist(user)
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

    @bridge.bridge_command(name="alerts", description="Enable or disable AFK messages")
    async def alerts(self, ctx):
        if await BlockUtils.get_perm("afkcheck", ctx.author) == True:
            await BlockUtils.remove_perm("afkcheck", ctx.author)
            e = discord.Embed(
                description=f"✅ Enabled AFK Alerts", color=0x66FF99)
            await utils.sendembed(ctx, e, False)
        else:
            await BlockUtils.add_perm("afkcheck", ctx.author)
            e = discord.Embed(
                description=f"❌ Disabled AFK Alerts", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="give", description=f"Give a permission to a user (use -permslist)")
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, user: discord.Member):
        perm = await BlockUtils.check_perm_arg(self, ctx)
        if await BlockUtils.get_perm(perm, user) == True:
            await utils.senderror(ctx, f"Nothing was changed.")
        else:
            await BlockUtils.add_perm(perm, user)
            e = discord.Embed(
                description=f"Gave {perm} to {user.mention}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="remove", description=f"Remove a permission from a user (use -permslist)")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, user: discord.Member):
        perm = await BlockUtils.check_perm_arg(self, ctx)
        if await BlockUtils.get_perm(perm, user) == False:
            await utils.senderror(ctx, f"Nothing was changed.")
        else:
            await BlockUtils.remove_perm(perm, user)
            e = discord.Embed(
                description=f"Removed {perm} from {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @commands.command(name="permslist", description=f"Lists all available permissions")
    @commands.has_permissions(administrator=True)
    async def permslist(self, ctx):
        e = discord.Embed(
            description=f"All available permissions", color=0x66FF99)
        perm_list = BlockUtils.get_perms_list()
        for perm, perm_desc in perm_list.items():
            e.add_field(name=f"{perm}", value=f"{perm_desc}", inline=False)
        await utils.sendembed(ctx, e, False)

    @commands.command(name="reset", description="Reset a user's permissions in the bot")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx, user: discord.Member):
        users = await BlockUtils.get_member_data()
        if str(user.id) in users:
            users.pop(str(user.id))
            yn = await BlockUtils.set_member_perms(users, user)
            if yn:
                await utils.sendembed(ctx, e=discord.Embed(description=f"Successfully reset {user.mention}", color=0x66FF99))
            else:
                await utils.senderror(ctx, f"Couldn't reset {user.mention}")
        else:
            await utils.senderror(ctx, "User isn't in data")
