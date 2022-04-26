import discord
import utils
from discord.ext import commands

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

    @commands.slash_command(name="help", description="Check PTRA's help page")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help1(self, ctx):
        e = await InfoUtils.helpuser(self, ctx)
        await ctx.respond(embed=e, ephemeral=True)
        if ctx.author.guild_permissions.administrator:
            e2 = await InfoUtils.helpadmin(self, ctx)
            await ctx.respond(embed=e2, ephemeral=True)

    @commands.command(name="help", description="Check PTRA's help page")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def help2(self, ctx):
        e = await InfoUtils.helpuser(self, ctx)
        await ctx.message.delete(delay=20.0)
        await ctx.reply(embed=e, delete_after=20.0, mention_author=False)
        if ctx.author.guild_permissions.administrator:
            e2 = await InfoUtils.helpadmin(self, ctx)
            await ctx.reply(embed=e2, delete_after=20.0, mention_author=False)

    @commands.slash_command(name="userinfo", description="Finds info about users.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def userinfo1(self, ctx, user: discord.Member):
        e = await InfoUtils.info(self, ctx, user)
        await ctx.respond(embed=e, ephemeral=True)

    @commands.command(name="userinfo", description="Finds info about users.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def userinfo2(self, ctx, user: discord.Member):
        e = await InfoUtils.info(self, ctx, user)
        await ctx.message.delete(delay=10.0)
        await ctx.reply(embed=e, delete_after=10.0, mention_author=False)

    @commands.command(name="ping", description="Tells you the bot's ping.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping1(self, ctx):
        e = await utils.ping(ctx)
        await ctx.message.delete(delay=10.0)
        await ctx.reply(embed=e, delete_after=10.0, mention_author=False)

    @commands.slash_command(name="ping", description="Tells you the bot's ping.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping2(self, ctx):
        e = await utils.ping(ctx)
        await ctx.respond(embed=e, ephemeral=True)

    @commands.command(name="installation", description="Sends the installation embeds.")
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def installation1(self, ctx, option=None):
        e1 = await InfoUtils.helpinstallembed(self, ctx)
        e2 = await InfoUtils.manualinstallembed(self, ctx)
        e3 = await InfoUtils.automaticinstallembed(self, ctx)
        await ctx.message.delete(delay=120.0)
        if ctx.author.guild_permissions.administrator and option == "channel":
            await ctx.message.delete()
            channel = ctx.guild.get_channel(922662496588943430)
            msg1 = await channel.fetch_message(968179173753516112)
            msg2 = await channel.fetch_message(968179174407831556)
            msg3 = await channel.fetch_message(968179175729012736)
            await msg1.edit(embed=e1)
            await msg2.edit(embed=e2)
            await msg3.edit(embed=e3)
            #await ctx.send(embed=e1)
            #await ctx.send(embed=e2)
            #await ctx.send(embed=e3)
        if option == "help":
            await ctx.reply(embed=e1, delete_after=120.0, mention_author=False)
        if option == "manual":
            await ctx.reply(embed=e2, delete_after=120.0, mention_author=False)
        if option == "automatic":
            await ctx.reply(embed=e3, delete_after=120.0, mention_author=False)
        if option == "both":
            await ctx.reply(embed=e1, delete_after=120.0, mention_author=False)
            await ctx.reply(embed=e2, delete_after=120.0, mention_author=False)
        if option == "all":
            await ctx.reply(embed=e1, delete_after=120.0, mention_author=False)
            await ctx.reply(embed=e2, delete_after=120.0, mention_author=False)
            await ctx.reply(embed=e3, delete_after=120.0, mention_author=False)
        if option != "channel" and option != "all" and option != "both" and option != "automatic" and option != "manual":
            await ctx.reply("Specify manual, automatic or both")

    @commands.slash_command(name="installation", description="Sends the installation embeds.")
    async def installation2(self, ctx, option: discord.Option(str, "What installation guide would you like to view?", choices=installation_options)):
        e1 = await InfoUtils.helpinstallembed(self, ctx)
        e2 = await InfoUtils.manualinstallembed(self, ctx)
        e3 = await InfoUtils.automaticinstallembed(self, ctx)
        if option == "help":
            await ctx.respond(embed=e1, ephemeral=True)
        if option == "manual":
            await ctx.respond(embed=e2, ephemeral=True)
        if option == "automatic":
            await ctx.respond(embed=e3, ephemeral=True)
        if option == "both":
            await ctx.respond(embed=e1, ephemeral=True)
            await ctx.respond(embed=e2, ephemeral=True)
        if option == "all":
            await ctx.respond(embed=e1, ephemeral=True)
            await ctx.respond(embed=e2, ephemeral=True)
            await ctx.respond(embed=e3, ephemeral=True)
        if option != "all" and option != "both" and option != "automatic" and option != "manual":
            await ctx.respond("Specify manual, automatic or both", ephemeral=True)

class InfoUtils():
    async def info(self, ctx, user: discord.Member):
        if user == None:
            user = ctx.author
        date_format = "%a, %d %b %Y %I:%M %p"
        e = discord.Embed(color=0xdfa3ff, description=user.mention)
        e.set_author(name=str(user), icon_url=user.avatar.url)
        e.set_thumbnail(url=user.avatar.url)
        e.add_field(name="Joined", value=user.joined_at.strftime(date_format))
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        e.add_field(name="Join position", value=str(members.index(user)+1))
        e.add_field(name="Registered",value=user.created_at.strftime(date_format))
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            e.add_field(name="Roles [{}]".format(len(user.roles)-1), value=role_string, inline=False)
        #perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        #e.add_field(name="Guild permissions", value=perm_string, inline=False) # way too big for my liking tbh
        e.set_footer(text='ID: ' + str(user.id))
        return e

    async def helpuser(self, ctx):
        e = discord.Embed(title="Help for PTRA bot", description="", color=0x69FFFF)
        e.add_field(name="/help or -help", value="Shows you this help page", inline=False)
        e.add_field(name="/installation or -installation", value="Shows you guides on how to install Northstar", inline=False)
        e.add_field(name="/suggest", value="used for making suggestions in <#951255789568409600> and <#952007443842469928>", inline=False)
        e.add_field(name="/ping or -ping", value="used for checking the bot's ping", inline=False)
        e.add_field(name="/userinfo or -userinfo", value="Shows you info about a user", inline=False)
        e.add_field(name="/afk or -afk", value="Sets an AFK for you, anyone pinging you will get a message saying you're AFK", inline=False)
        e.add_field(name="/gn or -gn", value="Same as AFK but it's goodnight \o/", inline=False)
        return e

    async def helpadmin(self, ctx):
        e = discord.Embed(title="Moderator only commands for MRVN bot", description="Commands that can only be used by moderators", color=0xFF6969)
        e.add_field(name="-approve domain sID", value="Approves suggestion, making it green and saying Approved", inline=False)
        e.add_field(name="-deny domain sID", value="Denies suggestion, making it red and saying Denied", inline=False)
        e.add_field(name="-note domain sID text", value="Adding a comment to a suggestion", inline=False)
        e.add_field(name="-block mention", value="Block a user to deny them from using the bot", inline=False)
        e.add_field(name="-unblock mention", value="Unblock a user to allow them to use the bot", inline=False)
        e.add_field(name="-reply text", value="Reply to someone's message with this command, it'll reply with the bot", inline=False)
        e.add_field(name="-dm user text", value="DM someone with the message saying your name", inline=False)
        e.add_field(name="-anondm user text", value="DM someone with the message not saying your name", inline=False)
        e.add_field(name="-reload", value="Restarts bot", inline=False)
        return e

    async def helpinstallembed(self, ctx):
        e = discord.Embed(title="Useful wiki help",description="Head over to the wiki and locate your issue/Q&A's", color=0xfffaac)
        e.add_field(name="Issues", value="[Can be fixed here](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting)\nIf you can't fix your issue yourself, [go to this message](https://discord.com/channels/920776187884732556/922663326994018366/967648724383838288) and open a ticket\nRemember to be honest in your ticket and provide as much information as possible", inline=False)
        e.add_field(name="Q&A", value="[Q&A's can be seen here](https://r2northstar.gitbook.io/r2northstar-wiki/faq)", inline=False)
        return e

    async def manualinstallembed(self, ctx):
        e = discord.Embed(title="Manual Installation for Northstar", description="you'll have to do this every update if you don't use a manager", color=0xFF6969)
        e.add_field(name="Download", value="[Download Northstar from this page](https://github.com/R2Northstar/Northstar/releases), pick the latest .zip", inline=False)
        e.add_field(name="Once Downloaded", value="1. Extract .zip's contents\n2. Drop files into the folder containing Titanfall2.exe\n3. Launch via [adding a launch option for your platform](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#launch-opts)\nYou can also launch using NorthstarLauncher.exe\nbut if you encounter errors, try the other option", inline=False)
        e.add_field(name="Launch the game!", value="GLHF Pilot!", inline=False)
        return e

    async def automaticinstallembed(self, ctx):
        e = discord.Embed(title="Automatic Installation for Northstar",description="Head over to an installer repository listed below", color=0x69FF69)
        e.add_field(name="VTOL", value="[Download the latest release and run the setup](https://github.com/BigSpice/VTOL/releases/latest/download/VTOL_Installer1.2.1.msi)\nLocate your game's folder and click Install Northstar", inline=False)
        e.add_field(name="Viper", value="[Click the big download button and run the setup](https://github.com/0neGal/viper#readme)\nLaunch Viper and click Launch!", inline=False)
        return e

