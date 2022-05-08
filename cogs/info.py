from typing import Optional
import discord
from discord.ext import commands, pages, bridge
from cogs import utils

installation_options = [
    discord.OptionChoice(name="help",
                         value="help"),
    discord.OptionChoice(name="manual",
                         value="manual"),
    discord.OptionChoice(name="automatic",
                         value="automatic"),
    discord.OptionChoice(name="both",
                         value="both"),
    discord.OptionChoice(name="all",
                         value="all")
]


class InfoCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @bridge.bridge_command(name="userinfo", description="Shows you information about users")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def userinfo(self, ctx, user: Optional[discord.Member]):
        user = user or ctx.author
        e = await InfoUtils.info(self, ctx, user)
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=20)

    @bridge.bridge_command(name="ping", description="Tells you the bot's ping.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        e = await utils.ping(ctx)
        await utils.sendembed(ctx, e, show_all=False, delete=3)

    @bridge.bridge_command(name="help", description="Shows you this help page")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help(self, ctx):
        paginator = pages.Paginator(pages=InfoUtils.get_pages(self, ctx))
        if ctx.author.guild_permissions.administrator:
            page_groups = [
                pages.PageGroup(
                    pages=InfoUtils.get_pages(self, ctx),
                    label="Main Commands",
                    description="Main Pages for commands that Members can use",
                ),
                pages.PageGroup(
                    pages=InfoUtils.get_pages_admin(self, ctx),
                    label="Moderator Commands",
                    description="Moderator Pages for commands that only Moderators can use",
                ),
            ]
            paginator = pages.Paginator(pages=page_groups, show_menu=True)
        if await utils.CheckInstance(ctx):
            try:
                await paginator.send(ctx, target=ctx.author)
                await ctx.reply("Check your DMs!", mention_author=False)
            except:
                await utils.senderror(ctx, "I couldn't DM you!")
        else:
            await paginator.respond(ctx.interaction, ephemeral=True)

    @bridge.bridge_command(name="installation", description="Shows you guides on how to install Northstar.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def installation(self, ctx):
        page_groups = [
            pages.PageGroup(
                pages=InfoUtils.get_pages_automatic(),
                label="Automatic Installation",
                description="",
            ),
            pages.PageGroup(
                pages=InfoUtils.get_pages_manual(),
                label="Manual Installation",
                description="",
            ),
            pages.PageGroup(
                pages=InfoUtils.get_pages_help(),
                label="Useful wiki help",
                description="Wiki Pages with useful information for fixing issues",
            ),
        ]
        paginator = pages.Paginator(
            pages=page_groups,
            show_menu=True,
            show_indicator=False,
            show_disabled=False)
        if await utils.CheckInstance(ctx):
            try:
                await paginator.send(ctx, target=ctx.author)
                await ctx.reply("Check your DMs!", mention_author=False)
            except:
                await utils.senderror(ctx, "I couldn't DM you!")
        else:
            await paginator.respond(ctx.interaction, ephemeral=True)

    @commands.command(name="adminstall", description="Shows you guides on how to install Northstar.")
    @commands.has_permissions(administrator=True)
    async def adminstall(self, ctx, option=None):
        e = [InfoUtils.get_pages_help()[0],
             InfoUtils.get_pages_manual()[0],
             InfoUtils.get_pages_automatic()[0],
             discord.Embed(description=f"{ctx.author.mention} just updated the installation embeds in <#922662496588943430>")]
        if option is not None:
            await utils.sendembed(ctx, e[3], show_all=False, delete=3, delete_speed=20)
            channel = ctx.guild.get_channel(922662496588943430)
            msg = [await channel.fetch_message(968179173753516112), await channel.fetch_message(968179174407831556), await channel.fetch_message(968179175729012736)]
            await msg[0].edit(embed=e[0])
            await msg[1].edit(embed=e[1])
            await msg[2].edit(embed=e[2])
        else:
            await ctx.send(embed=e[0])
            await ctx.send(embed=e[1])
            await ctx.send(embed=e[2])


class InfoUtils():
    def get_cmd_desc(self, ctx, cmd):
        for cog in self.ctx.cogs:
            for command in self.ctx.get_cog(cog).get_commands():
                if command.name == cmd:
                    return command.description

    def get_pages(self, ctx):
        pages = [
            discord.Embed(
                title="Help for PTRA bot",
                description="**Useful commands**", color=0x66FF99),
            discord.Embed(
                title="Help for PTRA bot",
                description="**User commands**", color=0xFF6969),
            discord.Embed(
                title="Help for PTRA bot",
                description="**Fun commands**", color=0x69FFFF),
        ]
        pages[0].add_field(
            name="/installation or -installation",
            value=InfoUtils.get_cmd_desc(self, ctx, "installation"),
            inline=True)
        pages[0].add_field(
            name="/suggest",
            value=InfoUtils.get_cmd_desc(self, ctx, "suggest"),
            inline=True)
        pages[0].add_field(
            name="/ping or -ping",
            value=InfoUtils.get_cmd_desc(self, ctx, "ping"),
            inline=True)
        pages[0].add_field(
            name="/userinfo or -userinfo",
            value=InfoUtils.get_cmd_desc(self, ctx, "userinfo"),
            inline=True)
        pages[0].add_field(
            name="/afk or -afk",
            value=InfoUtils.get_cmd_desc(self, ctx, "afk"),
            inline=True)
        pages[0].add_field(
            name="/gn or -gn",
            value=InfoUtils.get_cmd_desc(self, ctx, "gn"),
            inline=True)
        # pages[0].add_field(
        # name="/help or -help",
        # value=InfoUtils.get_cmd_desc(self, ctx, "help"),
        # inline=True)
        pages[1].add_field(
            name="/introvert or -introvert",
            value=InfoUtils.get_cmd_desc(self, ctx, "introvert"),
            inline=True)
        pages[1].add_field(
            name="/extrovert or -extrovert",
            value=InfoUtils.get_cmd_desc(self, ctx, "extrovert"),
            inline=True)
        pages[2].add_field(
            name="/pet or -pet",
            value=InfoUtils.get_cmd_desc(self, ctx, "pet"),
            inline=True)
        pages[2].add_field(
            name="/hug or -hug",
            value=InfoUtils.get_cmd_desc(self, ctx, "hug"),
            inline=True)
        pages[2].add_field(
            name="/kiss or -kiss",
            value=InfoUtils.get_cmd_desc(self, ctx, "kiss"),
            inline=True)
        pages[2].add_field(
            name="/fall or -fall",
            value=InfoUtils.get_cmd_desc(self, ctx, "fall"),
            inline=True)
        return pages

    def get_pages_admin(self, ctx):
        pages = [
            discord.Embed(
                title="Moderator only commands for MRVN bot",
                description="**Suggestion commands**", color=0x66FF99),
            discord.Embed(
                title="Moderator only commands for MRVN bot",
                description="**Permission commands**", color=0xFF6969),
            discord.Embed(
                title="Moderator only commands for MRVN bot",
                description="**Fun commands**", color=0x69FFFF),
            discord.Embed(
                title="Moderator only commands for MRVN bot",
                description="**Maintanance commands**", color=0xFFAC00),
        ]
        pages[0].add_field(
            name="-approve domain sID",
            value=InfoUtils.get_cmd_desc(self, ctx, "approve"),
            inline=True)
        pages[0].add_field(
            name="-deny domain sID",
            value=InfoUtils.get_cmd_desc(self, ctx, "deny"),
            inline=True)
        pages[0].add_field(
            name="-note domain sID text",
            value=InfoUtils.get_cmd_desc(self, ctx, "note"),
            inline=True)
        pages[1].add_field(
            name="-block mention",
            value=InfoUtils.get_cmd_desc(self, ctx, "block"),
            inline=True)
        pages[1].add_field(
            name="-unblock mention",
            value=InfoUtils.get_cmd_desc(self, ctx, "unblock"),
            inline=True)
        pages[1].add_field(
            name="-weird mention",
            value=InfoUtils.get_cmd_desc(self, ctx, "weird"),
            inline=True)
        pages[1].add_field(
            name="-unweird mention",
            value=InfoUtils.get_cmd_desc(self, ctx, "unweird"),
            inline=True)
        pages[2].add_field(
            name="-reply text",
            value=InfoUtils.get_cmd_desc(self, ctx, "reply"),
            inline=True)
        pages[2].add_field(
            name="-dm user text",
            value=InfoUtils.get_cmd_desc(self, ctx, "dm"),
            inline=True)
        pages[2].add_field(
            name="-namedm user text",
            value=InfoUtils.get_cmd_desc(self, ctx, "namedm"),
            inline=True)
        pages[2].add_field(
            name="-promote (mention optional) text",
            value=InfoUtils.get_cmd_desc(self, ctx, "promote"),
            inline=True)
        pages[2].add_field(
            name="-abuse",
            value=InfoUtils.get_cmd_desc(self, ctx, "abuse"),
            inline=True)
        pages[2].add_field(
            name="-noclip",
            value=InfoUtils.get_cmd_desc(self, ctx, "noclip"),
            inline=True)
        pages[3].add_field(
            name="-reload",
            value=InfoUtils.get_cmd_desc(self, ctx, "reload"),
            inline=True)
        return pages

    def get_pages_help():
        pages = [
            discord.Embed(
                title="Useful wiki help",
                description="**Head over to the wiki and locate your issue/Q&A's**", color=0xfffaac),
        ]
        pages[0].add_field(
            name="Q&A",
            value="[Q&A's can be seen here](https://r2northstar.gitbook.io/r2northstar-wiki/faq)",
            inline=False)
        pages[0].add_field(
            name="Issues",
            value="[Can be fixed here](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting)\nIf you can't fix your issue yourself, [go to this message](https://discord.com/channels/920776187884732556/922663326994018366/967648724383838288) and open a ticket\nRemember to be honest in your ticket and provide as much information as possible",
            inline=False)
        return pages

    def get_pages_manual():
        pages = [
            discord.Embed(
                title="Manual Installation for Northstar",
                description="**you'll have to do this every update if you don't use a manager**", color=0xFF6969)
        ]
        pages[0].add_field(
            name="Download",
            value="[Download Northstar from this page](https://github.com/R2Northstar/Northstar/releases), pick the latest .zip",
            inline=False)
        pages[0].add_field(
            name="Once Downloaded",
            value="1. Extract .zip's contents\n2. Drop files into the folder containing Titanfall2.exe\n3. Launch via [adding a launch option for your platform](https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/troubleshooting#launch-opts)\nYou can also launch using NorthstarLauncher.exe\nbut if you encounter errors, try the other option",
            inline=False)
        pages[0].add_field(
            name="Launch the game!",
            value="GLHF Pilot!",
            inline=False)
        return pages

    def get_pages_automatic():
        pages = [
            discord.Embed(
                title="Automatic Installation for Northstar",
                description="**Head over to an installer repository listed below**", color=0x69FF69)
        ]
        pages[0].add_field(
            name="R2Modman",
            value="[Click Manual Download\nInside the .zip run the related Setup.exe](https://northstar.thunderstore.io/package/ebkr/r2modman/)\nFollow the steps in the installer",
            inline=False)
        pages[0].add_field(
            name="VTOL",
            value="[Download the latest release\nRun the setup](https://github.com/BigSpice/VTOL/releases/latest/download/VTOL_Installer.msi)\nLocate your game's folder\nClick Install Northstar",
            inline=False)
        pages[0].add_field(
            name="Viper",
            value="[Download the latest release\nRun the setup](https://github.com/0neGal/viper#readme)\nLaunch Viper and click Launch!",
            inline=False)
        return pages

    async def info(self, ctx, user: discord.Member):
        date_format = "%a, %d %b %Y %I:%M %p"
        e = discord.Embed(color=0xdfa3ff, description=user.mention)
        e.set_author(name=str(user), icon_url=user.avatar.url)
        e.set_thumbnail(url=user.avatar.url)
        e.add_field(
            name="Joined",
            value=user.joined_at.strftime(date_format))
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        e.add_field(
            name="Join position",
            value=str(members.index(user)+1))
        e.add_field(
            name="Registered",
            value=user.created_at.strftime(date_format))
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            e.add_field(
                name="Roles [{}]".format(
                    len(user.roles)-1),
                value=role_string,
                inline=False)
        # perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        # e.add_field(
        # name="Guild permissions",
        # value=perm_string,
        # inline=False) # way too big for my liking tbh
        e.set_footer(text='ID: ' + str(user.id))
        return e
