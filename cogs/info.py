from typing import Optional
import discord
from discord.ext import commands, bridge
from cogs import utils

installation_options = [
    discord.OptionChoice(name="help", value="help"),
    discord.OptionChoice(name="manual", value="manual"),
    discord.OptionChoice(name="automatic", value="automatic"),
    discord.OptionChoice(name="both", value="both"),
    discord.OptionChoice(name="all", value="all")
]


class InfoCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @bridge.bridge_command(name="help", description="Check PTRA's help page")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help1(self, ctx):
        e = await InfoUtils.helpuser(self, ctx)
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=30)
        if ctx.author.guild_permissions.administrator:
            e2 = await InfoUtils.helpadmin(self, ctx)
            await utils.sendembed(ctx, e2, show_all=False, delete=3, delete_speed=30)

    @bridge.bridge_command(name="userinfo", description="Finds info about users.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def userinfo1(self, ctx, user: Optional[discord.Member]):
        user = user or ctx.author
        e = await InfoUtils.info(self, ctx, user)
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=20)

    @bridge.bridge_command(name="ping", description="Tells you the bot's ping.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping1(self, ctx):
        e = await utils.ping(ctx)
        await utils.sendembed(ctx, e, show_all=False, delete=3)

    @commands.command(name="installation", description="Sends the installation embeds.")
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def installation1(self, ctx, option=None):
        await ctx.message.delete(delay=120.0)
        help = await InfoUtils.helpinstallembed(self, ctx)
        manual = await InfoUtils.manualinstallembed(self, ctx)
        automatic = await InfoUtils.automaticinstallembed(self, ctx)
        if option not in ["channel", "help", "all", "both", "automatic", "manual"]:
            await ctx.reply("Specify manual, automatic or both", delete_after=10, mention_author=False)
            return
        elif option == "both":
            await ctx.reply(embed=manual, delete_after=120, mention_author=False)
            await ctx.reply(embed=automatic, delete_after=120, mention_author=False)
        elif option == "all":
            await ctx.reply(embed=help, delete_after=120, mention_author=False)
            await ctx.reply(embed=manual, delete_after=120, mention_author=False)
            await ctx.reply(embed=automatic, delete_after=120, mention_author=False)
        elif ctx.author.guild_permissions.administrator and option == "channel":
            await ctx.message.delete()
            channel = ctx.guild.get_channel(922662496588943430)
            msg1 = await channel.fetch_message(968179173753516112)
            msg2 = await channel.fetch_message(968179174407831556)
            msg3 = await channel.fetch_message(968179175729012736)
            await msg1.edit(embed=help)
            await msg2.edit(embed=manual)
            await msg3.edit(embed=automatic)
            # await ctx.send(embed=help)
            # await ctx.send(embed=manual)
            # await ctx.send(embed=automatic)
        else:
            option = await InfoUtils.EmbedOption(self, ctx, option)
            await ctx.reply(embed=option, delete_after=120, mention_author=False)

    @commands.slash_command(name="installation", description="Sends the installation embeds.")
    async def installation2(self, ctx, option: discord.Option(str, "What installation guide would you like to view?", choices=installation_options)):
        help = await InfoUtils.helpinstallembed(self, ctx)
        manual = await InfoUtils.manualinstallembed(self, ctx)
        automatic = await InfoUtils.automaticinstallembed(self, ctx)
        if option not in ["help", "all", "both", "automatic", "manual"]:
            await ctx.respond("Specify manual, automatic or both", ephemeral=True)
            return
        elif option == "both":
            await ctx.respond(embed=manual, ephemeral=True)
            await ctx.respond(embed=automatic, ephemeral=True)
        elif option == "all":
            await ctx.respond(embed=help, ephemeral=True)
            await ctx.respond(embed=manual, ephemeral=True)
            await ctx.respond(embed=automatic, ephemeral=True)
        else:
            e = await InfoUtils.EmbedOption(self, ctx, option)
            await ctx.respond(embed=e, ephemeral=True)


class InfoUtils():
    async def info(self, ctx, user: discord.Member):
        date_format = "%a, %d %b %Y %I:%M %p"
        e = discord.Embed(color=0xdfa3ff, description=user.mention)
        e.set_author(name=str(user), icon_url=user.avatar.url)
        e.set_thumbnail(url=user.avatar.url)
        e.add_field(name="Joined", value=user.joined_at.strftime(date_format))
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        e.add_field(name="Join position", value=str(members.index(user)+1))
        e.add_field(name="Registered",
                    value=user.created_at.strftime(date_format))
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            e.add_field(name="Roles [{}]".format(
                len(user.roles)-1), value=role_string, inline=False)
        #perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        # e.add_field(name="Guild permissions", value=perm_string, inline=False) # way too big for my liking tbh
        e.set_footer(text='ID: ' + str(user.id))
        return e

    async def helpuser(self, ctx):
        e = discord.Embed(title="Help for PTRA bot",
                          description="", color=0x69FFFF)
        e.add_field(name="/installation or -installation",
                    value="Shows you guides on how to install Northstar", inline=True)
        e.add_field(
            name="/suggest", value="Make a suggestion in\n<#951255789568409600>\nOr <#952007443842469928>", inline=True)
        e.add_field(name="/ping or -ping",
                    value="used for checking the bot's ping", inline=True)
        e.add_field(name="/userinfo or -userinfo",
                    value="Shows you info about a user", inline=True)
        e.add_field(name="/afk or -afk",
                    value="Alerts users that mention you that you're AFK", inline=True)
        e.add_field(name="/gn or -gn",
                    value="Same as AFK but it's goodnight \o/", inline=True)
        e.add_field(name="/help or -help",
                    value="Shows you this help page", inline=True)
        return e

    async def helpadmin(self, ctx):
        e = discord.Embed(title="Moderator only commands for MRVN bot",
                          description="Commands that can only be used by moderators", color=0xFF6969)
        e.add_field(name="-approve domain sID",
                    value="Approves suggestion, making it green and saying Approved", inline=True)
        e.add_field(name="-deny domain sID",
                    value="Denies suggestion, making it red and saying Denied", inline=True)
        e.add_field(name="-note domain sID text",
                    value="Adding a comment to a suggestion", inline=True)
        e.add_field(name="-block mention",
                    value="Block a user to deny them from using the bot", inline=True)
        e.add_field(name="-unblock mention",
                    value="Unblock a user to allow them to use the bot", inline=True)
        e.add_field(name="-weird mention",
                    value="Allow a user to use kiss, hug, pet, etc. commands", inline=True)
        e.add_field(name="-unweird mention",
                    value="Disallow a user to use kiss, hug, pet, etc. com", inline=True)
        e.add_field(name="-reply text",
                    value="Reply to someone's message with this command, it'll reply with the bot", inline=True)
        e.add_field(name="-dm user text",
                    value="DM someone with the message saying your name", inline=True)
        e.add_field(name="-anondm user text",
                    value="DM someone with the message not saying your name", inline=True)
        e.add_field(name="-reload", value="Restarts bot", inline=True)
        return e

    async def EmbedOption(self, ctx, option):
        if option == "manual":
            e = await InfoUtils.manualinstallembed(self, ctx)
            return e
        if option == "automatic":
            e = await InfoUtils.automaticinstallembed(self, ctx)
            return e
        if option == "help":
            e = await InfoUtils.helpinstallembed(self, ctx)
            return e

    async def helpinstallembed(self, ctx):
        e = discord.Embed(title="Useful wiki help",
                          description="Head over to the wiki and locate your issue/Q&A's", color=0xfffaac)
        e.add_field(
            name="Q&A", value="[Q&A's can be seen here](https://r2northstar.gitbook.io/r2northstar-wiki/faq)", inline=False)
        e.add_field(name="Issues", value="[Can be fixed here](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting)\nIf you can't fix your issue yourself, [go to this message](https://discord.com/channels/920776187884732556/922663326994018366/967648724383838288) and open a ticket\nRemember to be honest in your ticket and provide as much information as possible", inline=False)
        return e

    async def manualinstallembed(self, ctx):
        e = discord.Embed(title="Manual Installation for Northstar",
                          description="you'll have to do this every update if you don't use a manager", color=0xFF6969)
        e.add_field(
            name="Download", value="[Download Northstar from this page](https://github.com/R2Northstar/Northstar/releases), pick the latest .zip", inline=False)
        e.add_field(name="Once Downloaded",
                    value="1. Extract .zip's contents\n2. Drop files into the folder containing Titanfall2.exe\n3. Launch via [adding a launch option for your platform](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#launch-opts)\nYou can also launch using NorthstarLauncher.exe\nbut if you encounter errors, try the other option", inline=False)
        e.add_field(name="Launch the game!", value="GLHF Pilot!", inline=False)
        return e

    async def automaticinstallembed(self, ctx):
        e = discord.Embed(title="Automatic Installation for Northstar",
                          description="Head over to an installer repository listed below", color=0x69FF69)
        e.add_field(
            name="VTOL", value="[Download the latest release\nRun the setup](https://github.com/BigSpice/VTOL/releases/latest/download/VTOL_Installer1.2.1.msi)\nLocate your game's folder\nClick Install Northstar", inline=False)
        e.add_field(
            name="Viper", value="[Download the latest release\nRun the setup](https://github.com/0neGal/viper#readme)\nLaunch Viper and click Launch!", inline=False)
        return e
