import discord
from discord.ext import commands, bridge
from cogs import utils, configs


def setup(bot):
    bot.add_cog(BlockCommands(bot))


class BlockCommands(commands.Cog, name="Permissions"):
    """Commands for disallowing certain perms for certain things"""
    COG_EMOJI = "🔏"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(hidden=True, name="block")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def blacklist(self, ctx, user: discord.Member, *, reason=None):
        """Block a user to deny them from using the bot"""
        if await BlockCommands.get_perm(self, "blacklist", user):
            await ctx.reply("The person is already blacklisted.")
        else:
            await BlockCommands.add_perm(self, "blacklist", user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has blacklisted {user.mention} for: {reason}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(hidden=True, name="unblock")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unblacklist(self, ctx, user: discord.Member):
        """Unblock a user to allow them to use the bot"""
        if await BlockCommands.get_perm(self, "blacklist", user) == False:
            await ctx.reply("The person is already unblacklisted.")
        else:
            await BlockCommands.remove_perm(self, "blacklist", user)
            e = discord.Embed(
                description=f"{ctx.author.mention} has unblacklisted {user.mention}", color=0x66FF99)
            await utils.sendembed(ctx, e, False)

    @bridge.bridge_command(name="introvert")
    @commands.guild_only()
    async def introvert(self, ctx):
        """Toggle if people use fun commands like pet on you"""
        await BlockCommands.switch_perm(self, ctx, "ping", "Fun Commands on user")

    @bridge.bridge_command(name="alerts")
    async def alerts(self, ctx):
        """Toggle AFK messages"""
        await BlockCommands.switch_perm(self, ctx, "afk_alert", "AFK Alerts")

    @bridge.bridge_command(name="dmalerts")
    async def dmalerts(self, ctx):
        """Toggle AFK messages in DM instead"""
        if await utils.can_dm_user(ctx.author):
            await BlockCommands.switch_perm(self, ctx, "afk_alert_dm", "AFK Alerts in DMs instead")
        else:
            await utils.senderror(ctx, "I can't DM you! Try unblocking me or enabling your DMs.")

    @bridge.bridge_command(name="wbalerts")
    async def wbalerts(self, ctx):
        """Toggle Welcome Back message"""
        await BlockCommands.switch_perm(self, ctx, "wb_alert", "Welcome Back message")

    @bridge.bridge_command(name="wbdmalerts")
    async def wbdmalerts(self, ctx):
        """Toggle Welcome Back message in DM instead"""
        if await utils.can_dm_user(ctx.author):
            await BlockCommands.switch_perm(self, ctx, "wb_alert_dm", "Welcome Back message in DMs instead")
        else:
            await utils.senderror(ctx, "I can't DM you! Try unblocking me or enabling your DMs.")

    @commands.command(hidden=True, name="give")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def give(self, ctx, user: discord.Member):
        """Give a permission to a user (use -permslist)"""
        perm = await BlockCommands.check_perm_arg(self, ctx)
        if await BlockCommands.get_perm(self, ctx, perm, user):
            await utils.senderror(ctx, f"Nothing was changed.")
        else:
            await BlockCommands.add_perm(self, ctx, perm, user)
            e = discord.Embed(
                description=f"Gave {perm} to {user.mention}", color=0xFF6969)
            await utils.sendembed(ctx, e, False)

    @commands.command(hidden=True, name="remove")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove(self, ctx, user: discord.Member):
        """Remove a permission from a user (use -permslist)"""
        perm = await BlockCommands.check_perm_arg(self, ctx)
        if await BlockCommands.get_perm(self, ctx, perm, user) == False:
            await utils.senderror(ctx, f"Nothing was changed.")
        else:
            await BlockCommands.remove_perm(self, ctx, perm, user)
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
        for perm, perm_desc in self.ctx.perm_list.items():
            e.add_field(name=f"{perm}", value=f"{perm_desc}", inline=False)
        await utils.sendembed(ctx, e, False)

    @commands.command(hidden=True, name="reset")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset(self, ctx, user: discord.Member):
        """Reset a user's permissions in the bot"""
        perms = self.ctx.perms
        if str(user.id) in perms[str(user.guild.id)]:
            perms[str(user.guild.id)].pop(str(user.id))
            yn = await BlockCommands.set_member_perms(self, ctx, perms, user)
            if yn:
                await utils.sendembed(ctx, e=discord.Embed(description=f"Successfully reset {user.mention}", color=0x66FF99))
            else:
                await utils.senderror(ctx, f"Couldn't reset {user.mention}")
        else:
            await utils.senderror(ctx, "User isn't in data")

    async def open_member_perms(self, ctx, user):
        perms = self.ctx.perms
        if str(user.id) in perms[str(user.guild.id)]:
            return False
        else:
            await BlockCommands.set_member_perms(self, ctx, perms, user)

    async def open_perms(self, ctx, user):
        await BlockCommands.open_member_perms(self, ctx, user)
        return self.ctx.perms

    async def set_member_perms(self, ctx, perms, user):
        perms[str(user.guild.id)][str(user.id)] = {}
        for value in self.ctx.perms_list:
            perms[str(user.guild.id)][str(user.id)][value] = False
        configs.save(self.ctx.perms_path, "w", self.ctx.perms)
        return True

    async def get_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_perms(self, ctx, user)
        return perms[str(user.guild.id)][str(user.id)][perm]

    async def add_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_perms(self, ctx, user)
        perms[str(user.guild.id)][str(user.id)][perm] = True
        configs.save(self.ctx.perms_path, "w", self.ctx.perms)

    async def remove_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_perms(self, ctx, user)
        perms[str(user.guild.id)][str(user.id)][perm] = False
        configs.save(self.ctx.perms_path, "w", self.ctx.perms)

    async def check_perm_arg(self, ctx):
        perms_list = self.ctx.perms_list
        msg = ctx.message.content.split(" ")[2]
        if msg in perms_list:
            return msg
        else:
            await utils.senderror(ctx, f"{ctx.author.mention}, I couldn't find that permission.")

    async def switch_perm(self, ctx, perm, message):
        if await BlockCommands.get_perm(self, ctx, perm, ctx.author):
            await BlockCommands.remove_perm(self, ctx, perm, ctx.author)
            await utils.sendembed(ctx, discord.Embed(description=f"✅ Enabled {message}", color=0x66FF99), False)
        else:
            await BlockCommands.add_perm(self, ctx, perm, ctx.author)
            await utils.sendembed(ctx, discord.Embed(description=f"❌ Disabled {message}", color=0xFF6969), False)

    async def open_global_member_perms(self, ctx, user):
        perms = self.ctx.global_perms
        if str(user.id) in perms:
            return False
        else:
            await BlockCommands.set_global_member_perms(self, ctx, perms, user)

    async def set_global_member_perms(self, ctx, perms, user):
        perms[str(user.id)] = {}
        for value in self.ctx.global_perms_list_true:
            perms[str(user.id)][value] = True
        for value in self.ctx.global_perms_list_false:
            perms[str(user.id)][value] = False
        configs.save(self.ctx.global_perms_path, "w", perms)
        return True

    async def get_global_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_global_perm(self, ctx, user)
        return perms[str(user.id)][perm]

    async def add_global_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_global_perm(self, ctx, user)
        perms[str(user.id)][perm] = True
        configs.save(self.ctx.global_perms_path, "w", perms)

    async def remove_global_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_global_perm(self, ctx, user)
        perms[str(user.id)][perm] = False
        configs.save(self.ctx.global_perms_path, "w", perms)

    async def open_global_perm(self, ctx, user):
        await BlockCommands.open_global_member_perms(self, ctx, user)
        return self.ctx.global_perms

    async def switch_perm(self, ctx, perm, message):
        if await BlockCommands.get_global_perm(self, ctx, perm, ctx.author):
            await BlockCommands.remove_global_perm(self, ctx, perm, ctx.author)
            await utils.sendembed(ctx, discord.Embed(description=f"❌ Disabled {message}", color=0xFF6969), False)
        else:
            await BlockCommands.add_global_perm(self, ctx, perm, ctx.author)
            await utils.sendembed(ctx, discord.Embed(description=f"✅ Enabled {message}", color=0x66FF99), False)
