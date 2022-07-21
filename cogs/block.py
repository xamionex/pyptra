import discord
from discord.ext import commands, bridge
from cogs import configs
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(BlockCommands(bot))


class BlockCommands(commands.Cog, name="Permissions"):
    """Commands for disallowing certain perms for certain things"""
    COG_EMOJI = "🔏"

    def __init__(self, ctx):
        self.ctx = ctx

    @bridge.bridge_command(name="introvert")
    @commands.guild_only()
    async def introvert(self, ctx):
        """Toggle if people use fun commands like pet on you"""
        await BlockCommands.switch_perm(self, ctx, "ping", "Fun Commands on user")

    @bridge.bridge_command(name="alerts")
    async def alerts(self, ctx):
        """Toggle AFK messages"""
        await BlockCommands.switch_global_perm(self, ctx, "afk_alert", "AFK Alerts")

    @bridge.bridge_command(name="dmalerts")
    async def dmalerts(self, ctx):
        """Toggle AFK messages in DM instead"""
        if await Utils.can_dm_user(ctx.author):
            await BlockCommands.switch_global_perm(self, ctx, "afk_alert_dm", "AFK Alerts in DMs instead")
        else:
            await Utils.send_error(ctx, "I can't DM you! Try unblocking me or enabling your DMs.")

    @bridge.bridge_command(name="wbalerts")
    async def wbalerts(self, ctx):
        """Toggle Welcome Back message"""
        await BlockCommands.switch_global_perm(self, ctx, "wb_alert", "Welcome Back message")

    @bridge.bridge_command(name="wbdmalerts")
    async def wbdmalerts(self, ctx):
        """Toggle Welcome Back message in DM instead"""
        if await Utils.can_dm_user(ctx.author):
            await BlockCommands.switch_global_perm(self, ctx, "wb_alert_dm", "Welcome Back message in DMs instead")
        else:
            await Utils.send_error(ctx, "I can't DM you! Try unblocking me or enabling your DMs.")

    @commands.command(hidden=True, name="give", aliases=["add"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def give(self, ctx, user: discord.Member):
        """Give a permission to a user (use permslist command)"""
        perm = await BlockCommands.check_perm_arg(self, ctx)
        if await BlockCommands.get_perm(self, ctx, perm, user):
            await Utils.send_error(ctx, f"Nothing was changed.")
        else:
            await BlockCommands.add_perm(self, ctx, perm, user)
            string = f"Gave {perm} permission to {user.mention}" if self.ctx.settings[str(ctx.guild.id)]["invertperms"] else f"Unblocked {user.mention} from using {perm} commands" if perm not in self.ctx.perm_ignore_invert else f"Added {perm} to {user.mention}"
            await Utils.send_embed(ctx, discord.Embed(description=string, color=0xFF6969), False)

    @commands.command(hidden=True, name="take", aliases=["remove", "rem"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove(self, ctx, user: discord.Member):
        """Remove a permission from a user (use permslist command)"""
        perm = await BlockCommands.check_perm_arg(self, ctx)
        if await BlockCommands.get_perm(self, ctx, perm, user) == False:
            await Utils.send_error(ctx, f"Nothing was changed.")
        else:
            await BlockCommands.remove_perm(self, ctx, perm, user)
            string = f"Took {perm} permission from {user.mention}" if self.ctx.settings[str(ctx.guild.id)]["invertperms"] else f"Blocked {user.mention} from using {perm} commands" if perm not in self.ctx.perm_ignore_invert else f"Removed {perm} from {user.mention}"
            await Utils.send_embed(ctx, discord.Embed(description=string, color=0x66FF99), False)

    @commands.command(hidden=True, name="permslist")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def permslist(self, ctx):
        """Lists all available permissions"""
        e = discord.Embed(
            description=f"All available permissions", color=0x66FF99)
        for perm, perm_desc in self.ctx.perms_list.items():
            e.add_field(name=f"{perm}", value=f"{perm_desc}", inline=False)
        await Utils.send_embed(ctx, e)

    @commands.command(hidden=True, name="invertperms")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def invertperms(self, ctx):
        """Inverts all permissions (Whether perms block or allow)"""
        settings = self.ctx.settings[str(ctx.guild.id)]
        e = discord.Embed(description=f"Perms now act as Allowances.", color=0xFF6969).set_footer(text=f"Note that perms {', '.join(self.ctx.perm_ignore_invert)} ignore this")
        if settings["invertperms"]:
            settings["invertperms"] = False
            e.description = "Perms now act as Allowances"
            e.color = 0x66FF99
        else:
            settings["invertperms"] = True
            e.description = "Perms now act as Blockades"
            e.color = 0xFF6969
        await Utils.send_embed(ctx, e)
        configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    @commands.command(hidden=True, name="reset")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reset(self, ctx, user: discord.Member):
        """Reset a user's permissions in the bot"""
        perms = await BlockCommands.open_perms(self, ctx, user)
        ping = perms[str(user.id)]["ping"]
        perms.pop(str(user.id))
        try:
            perms[str(user.id)] = {}
            for value in self.ctx.perms_list:
                perms[str(user.id)][value] = False
            perms[str(user.id)]["ping"] = ping
            configs.save(self.ctx.settings_path, "w", self.ctx.settings)
            await Utils.send_embed(ctx, discord.Embed(description=f"Successfully reset {user.mention}", color=0x66FF99), False)
        except:
            await Utils.send_error(ctx, f"Couldn't reset {user.mention}")

    async def check_perm(self, ctx, permission, msg=None, dm=True):
        if ctx.author.guild_permissions.administrator:
            return
        perm = await BlockCommands.get_perm(self, ctx, permission, ctx.author)
        if permission not in self.ctx.perm_ignore_invert:
            if self.ctx.settings[str(ctx.guild.id)]["invertperms"]:
                perm = False if perm else True
        if not perm:
            string = f"You are missing {permission} permission to run this command." if self.ctx.settings[str(ctx.guild.id)]["invertperms"] else f"You are blocked from using {permission} commands."
            string = f"{string} (DM me to use this command freely.)" if dm else string
            await Utils.send_error(ctx, string, msg)

    async def check_ping(self, ctx, member, msg=None):
        if await BlockCommands.get_perm(self, ctx, "ping", member):
            await Utils.send_error(ctx, f"This person has disallowed me from using them in commands.", msg)

    async def open_member_perms(self, ctx, user):
        perms = self.ctx.settings[str(ctx.guild.id)]["perms"]
        if str(user.id) in perms:
            return perms
        else:
            await BlockCommands.set_member_perms(self, ctx, perms, user)

    async def open_perms(self, ctx, user):
        await BlockCommands.open_member_perms(self, ctx, user)
        return self.ctx.settings[str(ctx.guild.id)]["perms"]

    async def set_member_perms(self, ctx, perms, user):
        perms[str(user.id)] = {}
        for value in self.ctx.perms_list:
            perms[str(user.id)][value] = False
        configs.save(self.ctx.settings_path, "w", self.ctx.settings)
        return True

    async def get_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_perms(self, ctx, user)
        return perms[str(user.id)][str(perm)]

    async def add_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_perms(self, ctx, user)
        perms[str(user.id)][str(perm)] = True
        configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    async def remove_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_perms(self, ctx, user)
        perms[str(user.id)][str(perm)] = False
        configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    async def check_perm_arg(self, ctx):
        perms_list = self.ctx.perms_list
        try:
            msg = ctx.message.content.split(" ")[2]
        except:
            await Utils.send_error(ctx, "Specify a permission to change.")
        if msg == "ping":
            await Utils.send_error(ctx, "Changing ping toggle on users is a violation of their privacy.")
        elif msg in perms_list:
            return msg
        else:
            await Utils.send_error(ctx, f"{ctx.author.mention}, I couldn't find that permission.")

    async def switch_perm(self, ctx, perm, message):
        if await BlockCommands.get_perm(self, ctx, perm, ctx.author):
            await BlockCommands.remove_perm(self, ctx, perm, ctx.author)
            await Utils.send_embed(ctx, discord.Embed(description=f"✅ Enabled {message}", color=0x66FF99))
        else:
            await BlockCommands.add_perm(self, ctx, perm, ctx.author)
            await Utils.send_embed(ctx, discord.Embed(description=f"❌ Disabled {message}", color=0xFF6969))

    async def open_global_member_perms(self, ctx, user):
        perms = self.ctx.global_perms
        if str(user.id) in perms:
            return perms
        else:
            await BlockCommands.set_global_member_perms(self, ctx, perms, user)

    async def set_global_member_perms(self, ctx, perms, user):
        perms[str(user.id)] = {}
        for value in self.ctx.global_perms_list_true:
            perms[str(user.id)][value] = True
        for value in self.ctx.global_perms_list_false:
            perms[str(user.id)][value] = False
        configs.save(self.ctx.global_perms_path, "w", self.ctx.global_perms)
        return True

    async def get_global_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_global_perm(self, ctx, user)
        return perms[str(user.id)][str(perm)]

    async def add_global_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_global_perm(self, ctx, user)
        perms[str(user.id)][str(perm)] = True
        configs.save(self.ctx.global_perms_path, "w", self.ctx.global_perms)

    async def remove_global_perm(self, ctx, perm, user):
        perms = await BlockCommands.open_global_perm(self, ctx, user)
        perms[str(user.id)][str(perm)] = False
        configs.save(self.ctx.global_perms_path, "w", self.ctx.global_perms)

    async def open_global_perm(self, ctx, user):
        await BlockCommands.open_global_member_perms(self, ctx, user)
        return self.ctx.global_perms

    async def switch_global_perm(self, ctx, perm, message):
        if await BlockCommands.get_global_perm(self, ctx, perm, ctx.author):
            await BlockCommands.remove_global_perm(self, ctx, perm, ctx.author)
            await Utils.send_embed(ctx, discord.Embed(description=f"❌ Disabled {message}", color=0xFF6969))
        else:
            await BlockCommands.add_global_perm(self, ctx, perm, ctx.author)
            await Utils.send_embed(ctx, discord.Embed(description=f"✅ Enabled {message}", color=0x66FF99))
