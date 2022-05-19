import json
import discord
from discord.ext import commands, bridge
from cogs import utils


def setup(bot):
    bot.add_cog(BlockCommands(bot))


class BlockCommands(commands.Cog, name="Permissions"):
    """Commands for disallowing certain perms for certain things"""
    COG_EMOJI = "🔏"

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx

    @commands.command(hidden=True, name="block")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def blacklist(self, ctx, user: discord.Member, *, reason=None):
        """Block a user to deny them from using the bot"""
        if await BlockUtils.get_perm("blacklist", user):
            await ctx.reply("The person is already blacklisted.")
        else:
            await BlockUtils.add_perm("blacklist", user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has blacklisted {user.mention} for: {reason}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(hidden=True, name="unblock")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unblacklist(self, ctx, user: discord.Member):
        """Unblock a user to allow them to use the bot"""
        if await BlockUtils.get_perm("blacklist", user) == False:
            await ctx.reply("The person is already unblacklisted.")
        else:
            await BlockUtils.remove_perm("blacklist", user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has unblacklisted {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="introvert")
    @commands.guild_only()
    async def introvert(self, ctx):
        """Don't let people use commands like pet on you"""
        if await BlockUtils.get_perm("ping", ctx.author):
            await utils.senderror(ctx,
                                  f"I'm already not letting people use my commands with you.")
        else:
            await BlockUtils.add_perm("ping", ctx.author)
            e = discord.Embed(
                description=f"I wont let people use my commands with you", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="extrovert")
    @commands.guild_only()
    async def extrovert(self, ctx):
        """Let people use commands like pet on you"""
        if await BlockUtils.get_perm("ping", ctx.author) == False:
            await utils.senderror(ctx,
                                  f"I'm already letting people use my commands with you.")
        else:
            await BlockUtils.remove_perm("ping", ctx.author)
            e = discord.Embed(
                description=f"I'll let people use my commands with you", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="alerts")
    async def alerts(self, ctx):
        """Enable/disable AFK messages"""
        await GlobalBlockUtils.switch_perm(self, ctx, "afk_alert", "AFK Alerts")

    @bridge.bridge_command(name="dmalerts")
    async def dmalerts(self, ctx):
        """Enable/disable AFK messages in DM instead"""
        if await utils.can_dm_user(ctx.author):
            await GlobalBlockUtils.switch_perm(self, ctx, "afk_alert_dm", "AFK Alerts in DMs instead")
        else:
            await utils.senderror(ctx, "I can't DM you! Try unblocking me or enabling your DMs.")

    @bridge.bridge_command(name="wbalerts")
    async def wbalerts(self, ctx):
        """Enable/disable Welcome Back message"""
        await GlobalBlockUtils.switch_perm(self, ctx, "wb_alert", "Welcome Back message")

    @bridge.bridge_command(name="wbdmalerts")
    async def wbdmalerts(self, ctx):
        """Enable/disable Welcome Back message in DM instead"""
        if await utils.can_dm_user(ctx.author):
            await GlobalBlockUtils.switch_perm(self, ctx, "wb_alert_dm", "Welcome Back message in DMs instead")
        else:
            await utils.senderror(ctx, "I can't DM you! Try unblocking me or enabling your DMs.")

    @commands.command(hidden=True, name="give")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def give(self, ctx, user: discord.Member):
        """Give a permission to a user (use -permslist)"""
        perm = await BlockUtils.check_perm_arg(self, ctx)
        if await BlockUtils.get_perm(perm, user):
            await utils.senderror(ctx, f"Nothing was changed.")
        else:
            await BlockUtils.add_perm(perm, user)
            e = discord.Embed(
                description=f"Gave {perm} to {user.mention}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(hidden=True, name="remove")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove(self, ctx, user: discord.Member):
        """Remove a permission from a user (use -permslist)"""
        perm = await BlockUtils.check_perm_arg(self, ctx)
        if await BlockUtils.get_perm(perm, user) == False:
            await utils.senderror(ctx, f"Nothing was changed.")
        else:
            await BlockUtils.remove_perm(perm, user)
            e = discord.Embed(
                description=f"Removed {perm} from {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @commands.command(hidden=True, name="permslist")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def permslist(self, ctx):
        """Lists all available permissions"""
        e = discord.Embed(
            description=f"All available permissions", color=0x66FF99)
        perm_list = BlockUtils.get_perms_list()
        for perm, perm_desc in perm_list.items():
            e.add_field(name=f"{perm}", value=f"{perm_desc}", inline=False)
        await utils.sendembed(ctx, e, False)

    @commands.command(hidden=True, name="reset")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset(self, ctx, user: discord.Member):
        """Reset a user's permissions in the bot"""
        perms = await BlockUtils.get_perms_data()
        if str(user.id) in perms[str(user.guild.id)]:
            perms[str(user.guild.id)].pop(str(user.id))
            yn = await BlockUtils.set_member_perms(perms, user)
            if yn:
                await utils.sendembed(ctx, e=discord.Embed(description=f"Successfully reset {user.mention}", color=0x66FF99))
            else:
                await utils.senderror(ctx, f"Couldn't reset {user.mention}")
        else:
            await utils.senderror(ctx, "User isn't in data")


class BlockUtils():
    async def get_perms_data():
        with open("./data/perms.json") as f:
            perms = json.load(f)
            return perms

    async def open_member_perms(user):
        perms = await BlockUtils.get_perms_data()
        if str(user.id) in perms[str(user.guild.id)]:
            return False
        else:
            await BlockUtils.set_member_perms(perms, user)

    def get_perms_list():
        perms = {"blacklist": "Denies usage for bot",
                 "weird": "Allows -hug -kiss",
                 "ping": "Denies pinging user in -hug -kiss -pet",
                 "pet": "Allows petting users/images/emojis",
                 "joke": "Allows using -fall -promote"}
        return perms

    async def set_member_perms(perms, user):
        perms[str(user.guild.id)][str(user.id)] = {}
        perms_list = BlockUtils.get_perms_list()
        for value in perms_list:
            perms[str(user.guild.id)][str(user.id)][value] = False
        with open("./data/perms.json", "w") as f:
            json.dump(perms, f, indent=4, sort_keys=True)
            return True

    async def get_perm(perm, user):
        perms = await BlockUtils.open_perms(user)
        return perms[str(user.guild.id)][str(user.id)][perm]

    async def add_perm(perm, user):
        perms = await BlockUtils.open_perms(user)
        perms[str(user.guild.id)][str(user.id)][perm] = True
        await BlockUtils.dump(perms)

    async def remove_perm(perm, user):
        perms = await BlockUtils.open_perms(user)
        perms[str(user.guild.id)][str(user.id)][perm] = False
        await BlockUtils.dump(perms)

    async def open_perms(user):
        await BlockUtils.open_member_perms(user)
        return await BlockUtils.get_perms_data()

    async def check_perm_arg(self, ctx):
        perms_list = BlockUtils.get_perms_list()
        msg = ctx.message.content.split(" ")[2]
        if msg in perms_list:
            return msg
        else:
            await utils.senderror(ctx, f"{ctx.author.mention}, I couldn't find that permission.")

    async def switch_perm(self, ctx, perm, message):
        if await BlockUtils.get_perm(perm, ctx.author):
            await BlockUtils.remove_perm(perm, ctx.author)
            e = discord.Embed(
                description=f"✅ Enabled {message}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)
        else:
            await BlockUtils.add_perm(perm, ctx.author)
            e = discord.Embed(
                description=f"❌ Disabled {message}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    async def dump(perms):
        with open("./data/perms.json", "w") as f:
            json.dump(perms, f, indent=4, sort_keys=True)


class GlobalBlockUtils():
    async def get_global_perms_data():
        with open("./data/global_perms.json") as f:
            perms = json.load(f)
            return perms

    async def open_global_member_perms(user):
        perms = await GlobalBlockUtils.get_global_perms_data()
        if str(user.id) in perms:
            return False
        else:
            await GlobalBlockUtils.set_global_member_perms(perms, user)

    def get_global_perms_list():
        perms = {"wb_alert_dm": "Disables/Enables welcome back embed sending in DM instead",
                 "afk_alert_dm": "Disables/Enables AFK alerts sending in DM instead"}
        invert_perms = {"wb_alert": "Disables/Enables welcome back embed, overrides DM",
                        "afk_alert": "Disables/Enables AFK alerts, overrides DM", }
        return invert_perms, perms

    async def set_global_member_perms(perms, user):
        perms[str(user.id)] = {}
        perms_list = GlobalBlockUtils.get_global_perms_list()
        for value in perms_list[0]:
            perms[str(user.id)][value] = True
        for value in perms_list[1]:
            perms[str(user.id)][value] = False
        with open("./data/global_perms.json", "w") as f:
            json.dump(perms, f, indent=4, sort_keys=True)
            return True

    async def get_global_perm(perm, user):
        perms = await GlobalBlockUtils.open_global_perm(user)
        return perms[str(user.id)][perm]

    async def add_global_perm(perm, user):
        perms = await GlobalBlockUtils.open_global_perm(user)
        perms[str(user.id)][perm] = True
        await GlobalBlockUtils.dump(perms)

    async def remove_global_perm(perm, user):
        perms = await GlobalBlockUtils.open_global_perm(user)
        perms[str(user.id)][perm] = False
        await GlobalBlockUtils.dump(perms)

    async def open_global_perm(user):
        await GlobalBlockUtils.open_global_member_perms(user)
        return await GlobalBlockUtils.get_global_perms_data()

    async def switch_perm(self, ctx, perm, message):
        if await GlobalBlockUtils.get_global_perm(perm, ctx.author):
            await GlobalBlockUtils.switch_perm_remove(self, ctx, perm, message)
        else:
            await GlobalBlockUtils.switch_perm_add(self, ctx, perm, message)

    async def switch_perm_remove(self, ctx, perm, message):
        await GlobalBlockUtils.remove_global_perm(perm, ctx.author)
        await utils.sendembed(ctx, discord.Embed(description=f"❌ Disabled {message}", color=0xFF6969), False)

    async def switch_perm_add(self, ctx, perm, message):
        await GlobalBlockUtils.add_global_perm(perm, ctx.author)
        await utils.sendembed(ctx, discord.Embed(description=f"✅ Enabled {message}", color=0x66FF99), False)

    async def dump(perms):
        with open("./data/global_perms.json", "w") as f:
            json.dump(perms, f, indent=4, sort_keys=True)
