import json
import discord
from discord.ext import commands, bridge
from cogs import utils, block, configs
# afk command data
import time


def setup(bot):
    bot.add_cog(UserCommands(bot))


class UserCommands(commands.Cog, name="User Commands"):
    """User commands, mostly information."""
    COG_EMOJI = "👤"

    def __init__(self, ctx):
        self.ctx = ctx

    @bridge.bridge_command(name="rep")
    async def rep(self, ctx, user: discord.Member, type=None):
        """Add a reputation to a user."""
        if type not in self.ctx.rep_type_combined:
            e = discord.Embed(
                description="`❌` You must pick one of these for the type of rep:", color=0xFF6969)
            e.add_field(
                name="Positive", value=f"`{'`, `'.join(self.ctx.rep_type_positive)}`")
            e.add_field(
                name="Negative", value=f"`{'`, `'.join(self.ctx.rep_type_negative)}`")
            e.set_footer(
                text=f"For stats type {self.ctx.guild_prefixes[str(ctx.guild.id)]}repstats @user")
            await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=15)
            return
        elif type in self.ctx.rep_type_positive:
            if user.id == ctx.author.id:
                await utils.senderror(ctx, "You can't give rep to yourself")
            else:
                await UserUtils.change_rep(self, ctx, "positive", user)
                await utils.sendembed(ctx, discord.Embed(description=f"`➕` Giving {user.mention} positive rep"), show_all=False, delete=3, delete_speed=5)
        elif type in self.ctx.rep_type_negative:
            if user.id == ctx.author.id:
                await utils.senderror(ctx, "You can't give rep to yourself")
            else:
                await UserUtils.change_rep(self, ctx, "negative", user)
                await utils.sendembed(ctx, discord.Embed(description=f"`➖` Giving {user.mention} negative rep"), show_all=False, delete=3, delete_speed=5)

    @bridge.bridge_command(name="repstats")
    async def repstats(self, ctx, user: discord.Member):
        rep = await UserUtils.get_rep(self, ctx, user)
        e = discord.Embed(description=f"{user.mention}'s reputation:")
        e.add_field(name="Final Reputation", value=rep[0], inline=False)
        e.add_field(name="Positive Reputation", value=rep[1], inline=False)
        e.add_field(name="Negative Reputation", value=rep[2], inline=False)
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=5)

    @bridge.bridge_command(name="afk")
    async def afk(self, ctx, *, reason=None):
        """Alerts users that mention you that you're AFK."""
        if reason:
            reason = utils.remove_newlines(reason)
        e = await UserUtils.setafk(self, ctx, reason)
        await UserUtils.sendafk(self, ctx, ["afk_alert", "afk_alert_dm"], e)

    @bridge.bridge_command(name="gn")
    async def gn(self, ctx):
        """Sets your AFK to `Sleeping 💤`"""
        await UserUtils.setafk(self, ctx, "Sleeping 💤")
        e = discord.Embed(description=f"Goodnight {ctx.author.mention}")
        e.set_image(url="https://c.tenor.com/nPYfVs6FsBQAAAAS/kitty-kitten.gif")
        await UserUtils.sendafk(self, ctx, ["afk_alert", "afk_alert_dm"], e)


class UserUtils():
    def __init__(self, ctx):
        self.ctx = ctx

    async def open_member_rep(self, ctx, user):
        rep = self.ctx.reputation
        if str(user.id) in rep:
            return False
        else:
            await UserUtils.set_rep(self, ctx, rep, user)

    async def set_rep(self, ctx, rep, user):
        rep[str(user.id)] = {}
        for value in self.ctx.rep_type_list:
            rep[str(user.id)][value] = 0
        configs.save(self.ctx.reputation_path, "w", rep)
        return True

    async def get_rep(self, ctx, user):
        rep = await UserUtils.open_rep(self, ctx, user)
        current_rep = rep[str(user.id)]["positive"] - \
            rep[str(user.id)]["negative"]
        reps = [current_rep,
                rep[str(user.id)]["positive"],
                rep[str(user.id)]["negative"]]
        return reps

    async def change_rep(self, ctx, change, user):
        rep = await UserUtils.open_rep(self, ctx, user)
        rep[str(user.id)][change] += 1
        configs.save(self.ctx.reputation_path, "w", rep)

    async def open_rep(self, ctx, user):
        await UserUtils.open_member_rep(self, ctx, user)
        return self.ctx.reputation

    async def setafk(self, ctx, reason):
        afk = self.ctx.afk
        if not reason:
            reason = 'AFK'
        elif reason and len(reason) > 100:
            await utils.senderror(ctx, "You went over the 100 character limit")
        await UserUtils.update_data(afk, ctx.author)
        afk[f'{ctx.author.id}']['reason'] = f'{reason}'
        if afk[f'{ctx.author.id}']['AFK']:
            rply = discord.Embed(
                description=f"Goodbye {ctx.author.mention}, Updated alert to \"{reason}\"")
        else:
            afk[f'{ctx.author.id}']['AFK'] = True
            afk[f'{ctx.author.id}']['time'] = int(time.time())
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

    async def update_data(afk, user):
        if not f'{user.id}' in afk:
            afk[f'{user.id}'] = {}
            afk[f'{user.id}']['AFK'] = False

    def period(delta, pattern):
        d = {'d': delta.days}
        d['h'], rem = divmod(delta.seconds, 3600)
        d['m'], d['s'] = divmod(rem, 60)
        return pattern.format(**d)

    async def sendafk(self, ctx, perm, e):
        if await block.GlobalBlockUtils.get_global_perm(self, ctx, perm[0], ctx.author):
            if await block.GlobalBlockUtils.get_global_perm(self, ctx, perm[1], ctx.author):
                await utils.senddmembed(ctx, e)
            else:
                if isinstance(ctx, bridge.BridgeApplicationContext):
                    await ctx.reply(embed=e, ephemeral=True)
                else:
                    await ctx.reply(embed=e, delete_after=10, mention_author=False)
