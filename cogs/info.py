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


def setup(bot):
    bot.add_cog(InfoCommands(bot))


class InfoCommands(commands.Cog, name="Informational"):
    """Commands that show you general information about multiple things."""
    COG_EMOJI = "ℹ️"

    def __init__(self, ctx):
        self.ctx = ctx

    @bridge.bridge_command(name="userinfo")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def userinfo(self, ctx, user: Optional[discord.Member]):
        """Shows you information about users"""
        user = user or ctx.author
        date = [utils.iso8601_to_epoch(user.joined_at.isoformat(
        )), utils.iso8601_to_epoch(user.created_at.isoformat())]
        e = discord.Embed(color=0xdfa3ff, description=user.mention)
        e.set_author(name=str(user), icon_url=user.avatar.url)
        e.set_thumbnail(url=user.avatar.url)
        e.add_field(
            name="Joined",
            value=f"<t:{date[0]}:f> (<t:{date[0]}:R>)", inline=False)
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        e.add_field(
            name="Registered",
            value=f"<t:{date[1]}:f> (<t:{date[1]}:R>)", inline=False)
        e.add_field(
            name="Join position",
            value=str(members.index(user)+1))
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
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=20)

    @bridge.bridge_command(name="pfp")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def pfp(self, ctx, user: Optional[discord.Member]):
        """Shows you an users profile picture"""
        user = user or ctx.author
        e = discord.Embed(
            color=0xdfa3ff, description=f'{user.mention} - [Link to profile picture]({user.avatar.url})')
        e.set_image(url=user.avatar.url)
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=20)

    @bridge.bridge_command(name="ping")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        """Tells you the bot's ping."""
        e = await utils.ping(ctx)
        await utils.sendembed(ctx, e, show_all=False, delete=3)

    @bridge.bridge_command(name="installation")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def installation(self, ctx):
        """Shows you guides on how to install Northstar."""
        page_groups = [
            pages.PageGroup(
                pages=self.get_pages_automatic(),
                label="Automatic Installation",
                description="",
            ),
            pages.PageGroup(
                pages=self.get_pages_manual(),
                label="Manual Installation",
                description="",
            ),
            pages.PageGroup(
                pages=self.get_pages_help(),
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

    @commands.command(hidden=True, name="adminstall")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def adminstall(self, ctx, option=None):
        """Shows you guides on how to install Northstar."""
        e = [self.get_pages_help()[0],
             self.get_pages_manual()[0],
             self.get_pages_automatic()[0],
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

    def get_pages_help(self):
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

    def get_pages_manual(self):
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

    def get_pages_automatic(self):
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
