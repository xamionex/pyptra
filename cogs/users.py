import json
import re
import discord
from discord.ext import commands, bridge
from cogs.configs import Configs
from cogs.block import BlockCommands
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(UserCommands(bot))


class UserCommands(commands.Cog, name="User Commands"):
    """User commands, mostly information."""
    COG_EMOJI = "👤"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.group(hidden=True, name="rep", invoke_without_command=True)
    async def rep(self, ctx):
        """Reputation commands for users"""
        await Utils.send_error(ctx, f"No command specified, do {self.ctx.settings[str(ctx.guild.id)]['prefix']}help rep for more info")

    @rep.command(name="give")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def give(self, ctx, user: discord.Member = None, type=None):
        """Give reputation to a user."""
        if user is None:
            e = self.rep_embed(ctx, "give")
            await ctx.respond(embed=e)
            ctx.command.reset_cooldown(ctx)
            return
        if type not in self.ctx.rep_type_combined:
            e = self.rep_embed(ctx, "give")
            await ctx.respond(embed=e)
            ctx.command.reset_cooldown(ctx)
            return
        elif type in self.ctx.rep_type_positive:
            if user.id == ctx.author.id:
                await Utils.send_error(ctx, "You can't give rep to yourself")
            else:
                await self.change_rep(ctx, "positive", user)
                await ctx.respond(embed=discord.Embed(description=f"`➕` Giving {user.mention} positive rep"))
        elif type in self.ctx.rep_type_negative:
            if user.id == ctx.author.id:
                await Utils.send_error(ctx, "You can't give rep to yourself")
            else:
                await self.change_rep(ctx, "negative", user)
                await ctx.respond(embed=discord.Embed(description=f"`➖` Giving {user.mention} negative rep"))

    @rep.command(name="take")
    async def take(self, ctx, user: discord.Member = None, type=None):
        """Remove reputation from a user."""
        if user is None:
            e = self.rep_embed(ctx, "take")
            await ctx.respond(embed=e)
            ctx.command.reset_cooldown(ctx)
            return
        if type not in self.ctx.rep_type_combined:
            e = self.rep_embed(ctx, "take")
            await ctx.respond(embed=e)
            ctx.command.reset_cooldown(ctx)
            return
        elif type in self.ctx.rep_type_positive:
            if user.id == ctx.author.id:
                await Utils.send_error(ctx, "You can't give rep to yourself")
            else:
                await self.rem_rep(ctx, "positive", user)
                await ctx.respond(embed=discord.Embed(description=f"`➕` Removing your positive rep from {user.mention}"))
        elif type in self.ctx.rep_type_negative:
            if user.id == ctx.author.id:
                await Utils.send_error(ctx, "You can't give rep to yourself")
            else:
                await self.rem_rep(ctx, "negative", user)
                await ctx.respond(embed=discord.Embed(description=f"`➖` Removing your negative rep from {user.mention}"))

    @rep.command(name="show")
    async def show(self, ctx, user: discord.Member = None):
        """Show a user's reputation"""
        user = user or ctx.author
        rep = await self.get_rep(ctx, user)
        e = discord.Embed(description=f"{user.mention}'s reputation:")
        e.add_field(name="Final Reputation", value=rep[0], inline=False)
        e.add_field(name="Positive Reputation", value=rep[1], inline=False)
        e.add_field(name="Negative Reputation", value=rep[2], inline=False)
        await ctx.respond(embed=e)

    @rep.command(name="everyone")
    async def showall(self, ctx):
        """Shows global reputation of users"""
        p, n = 0, 0
        for user in self.ctx.reputation.items():
            p += len(user[1]["positive"])
            n += len(user[1]["negative"])
        f = p - n
        e = discord.Embed(description=f"**Global reputation:**")
        e.add_field(name="Final Reputation", value=f, inline=False)
        e.add_field(name="Positive Reputation", value=p, inline=False)
        e.add_field(name="Negative Reputation", value=n, inline=False)
        await ctx.respond(embed=e)

    @commands.command(hidden=True, name="resetrep")
    @commands.is_owner()
    async def resetrep(self, ctx, user: discord.Member = None):
        """Reset a user's reputation"""
        user = user or ctx.author
        rep = await UserCommands.open_rep(self, ctx, user)
        rep.pop(str(user.id))
        try:
            await self.set_rep(ctx, rep, user)
            await ctx.respond(embed=discord.Embed(description=f"Successfully reset {user.mention}", color=0x66FF99))
        except:
            await Utils.send_error(ctx, f"Couldn't reset {user.mention}")

    @bridge.bridge_command(name="afk")
    async def afk(self, ctx, *, reason=None):
        """Alerts users that mention you that you're AFK."""
        if reason:
            reason = Utils.remove_newlines(reason)
        e = await UserCommands.setafk(self, ctx, reason)
        await UserCommands.sendafk(self, ctx, ["afk_alert", "afk_alert_dm"], e)

    @bridge.bridge_command(name="hex", aliases=["color", "colour"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def color(self, ctx, *, hex):
        """Gives you a color based on the hex you gave."""
        await BlockCommands.check_perm(self, ctx, "hex", dm=False)
        hex = hex.replace("0x", "", 1) if hex.startswith("0x") else hex
        hex = ''.join(re.findall("[\da-f]+", Utils.strip_accents(hex), re.IGNORECASE))
        if len(hex) < 6:
            await Utils.send_error(ctx, "Please enter a six digit hex number. (ex. #133769)")
        hex = hex[0:6]
        rolename = f"#{hex}"
        rolecolor = discord.Colour(int(f"0x{hex}", 16))
        for role in ctx.author.roles:
            if rolename == role.name:
                has_already = True
                break
            else:
                has_already = False
        if not has_already:
            for role in ctx.guild.roles:
                if rolename == role.name:
                    found = True
                    await ctx.author.add_roles(role)
                    break
                else:
                    found = False
            if not found:
                role = await ctx.guild.create_role(name=rolename, color=rolecolor)
                await role.edit(position=ctx.guild.get_member(self.ctx.user.id).top_role.position - 1)
                await ctx.author.add_roles(role)
                await ctx.respond(embed=discord.Embed(description=f"`✅` Added {role.name} and gave it to {ctx.author.mention}", color=rolecolor))
            elif found:
                await ctx.respond(embed=discord.Embed(description=f"`✅` Gave {role.name} to {ctx.author.mention}", color=rolecolor))
        else:
            for role in ctx.guild.roles:
                if rolename == role.name:
                    await ctx.author.remove_roles(role)
                    if len(role.members) == 0:
                        await role.delete(reason="No-one had the role assigned anymore")
                        await ctx.respond(embed=discord.Embed(description=f"`❌` Deleted {role.name} as no-one was using it now", color=rolecolor))
                    else:
                        await ctx.respond(embed=discord.Embed(description=f"`❌` Took {role.name} from {ctx.author.mention}", color=rolecolor))

    @bridge.bridge_command(name="gn")
    async def gn(self, ctx):
        """Sets your AFK to `Sleeping 💤`"""
        await UserCommands.setafk(self, ctx, "Sleeping 💤")
        e = discord.Embed(description=f"Goodnight {ctx.author.mention}")
        e.set_image(url="https://c.tenor.com/nPYfVs6FsBQAAAAS/kitty-kitten.gif")
        await UserCommands.sendafk(self, ctx, ["afk_alert", "afk_alert_dm"], e)

    async def open_member_rep(self, ctx, user):
        rep = self.ctx.reputation
        if str(user.id) in rep:
            return False
        else:
            await self.set_rep(ctx, rep, user)

    async def set_rep(self, ctx, rep, user):
        rep[str(user.id)] = {}
        for value in self.ctx.rep_type_list:
            rep[str(user.id)][value] = []
        Configs.save(self.ctx.reputation_path, "w", rep)
        return True

    async def get_rep(self, ctx, user):
        rep = await UserCommands.open_rep(self, ctx, user)
        p = len(rep[str(user.id)]["positive"])
        n = len(rep[str(user.id)]["negative"])
        u = p - n
        reps = [u, p, n]
        return reps

    async def change_rep(self, ctx, change, user):
        rep = await UserCommands.open_rep(self, ctx, user)
        if str(ctx.author.id) in rep[str(user.id)][change]:
            await Utils.send_error(ctx, f"You already gave this person {change} rep\nIf you want to remove it take a look at {self.ctx.settings[str(ctx.guild.id)]['prefix']}help rep")
        else:
            rep[str(user.id)][change].append(str(ctx.author.id))
        Configs.save(self.ctx.reputation_path, "w", rep)

    async def rem_rep(self, ctx, change, user):
        rep = await UserCommands.open_rep(self, ctx, user)
        try:
            rep[str(user.id)][change].remove(str(ctx.author.id))
        except:
            await Utils.send_error(ctx, f"You don't have {change} rep on this person")
        Configs.save(self.ctx.reputation_path, "w", rep)

    async def open_rep(self, ctx, user):
        await UserCommands.open_member_rep(self, ctx, user)
        return self.ctx.reputation

    async def setafk(self, ctx, reason):
        afk = self.ctx.afk
        if not reason:
            reason = 'AFK'
        elif reason and len(reason) > 169:
            await Utils.send_error(ctx, "You went over the 169 character limit")
        await self.open_user(afk, ctx.author)
        afk[f'{ctx.author.id}']['reason'] = f'{reason}'
        if afk[f'{ctx.author.id}']['AFK']:
            rply = discord.Embed(
                description=f"Goodbye {ctx.author.mention}, Updated alert to \"{reason}\"")
        else:
            afk[f'{ctx.author.id}']['AFK'] = True
            afk[f'{ctx.author.id}']['time'] = Utils.current_milli_time()
            afk[f'{ctx.author.id}']['mentions'] = 0
            rply = discord.Embed(
                description=f"Goodbye {ctx.author.mention}, Set alert to \"{reason}\"")
            try:
                await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
            except:
                pass
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)
        return rply

    async def open_user(self, afk, user):
        if not f'{user.id}' in afk:
            afk[f'{user.id}'] = {}
            afk[f'{user.id}']['AFK'] = False

    async def sendafk(self, ctx, perm, e):
        if await BlockCommands.get_global_perm(self, ctx, perm[0], ctx.author):
            if await BlockCommands.get_global_perm(self, ctx, perm[1], ctx.author):
                try:
                    await ctx.author.send(embed=e)
                except:
                    await ctx.respond(embed=e)
            else:
                await ctx.respond(embed=e)

    def rep_embed(self, ctx, type):
        e = discord.Embed(title=f"{self.ctx.settings[str(ctx.guild.id)]['prefix']}rep {type} <mention> <type>",
                          description="`❌` **You must mention someone and pick one of these for the type of rep:**", color=0xFF6969)
        e.add_field(
            name="Positive", value=f"`{'`, `'.join(self.ctx.rep_type_positive)}`")
        e.add_field(
            name="Negative", value=f"`{'`, `'.join(self.ctx.rep_type_negative)}`")
        e.set_footer(
            text=f"For stats type {self.ctx.settings[str(ctx.guild.id)]['prefix']}show @user or {self.ctx.settings[str(ctx.guild.id)]['prefix']}rep everyone")
        return e
