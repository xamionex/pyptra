import time
from typing import Optional
import discord
from discord.ext import commands, pages, bridge
from cogs.configs import Configs
from cogs.utils import Utils

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

    @bridge.bridge_command(name="serverinfo", aliases=["si", "sid"])
    @commands.guild_only()
    @commands.cooldown(1, 420, commands.BucketType.user)
    async def serverinfo(self, ctx):
        """Shows you information about the server"""
        fetch_guild = await self.ctx.fetch_guild(int(ctx.guild.id), with_counts=True)
        registered = Utils.iso8601_to_epoch(ctx.guild.created_at.isoformat())
        e = discord.Embed(title=ctx.guild.name, description=f"2FA Needed for moderation: {'✅' if ctx.guild.mfa_level == 1 else '❎'}", color=discord.Colour.blue())
        e.set_author(name=f"Owned by {ctx.guild.owner.name}", url=ctx.guild.owner.jump_url, icon_url=ctx.guild.owner.display_avatar if ctx.guild.owner.display_avatar is not None else "https://cdn.discordapp.com/emojis/969684646906437643.webp?size=96&quality=lossless")
        e.set_thumbnail(url=ctx.guild.icon.url) if ctx.guild.icon.url is not None else None
        e.add_field(name="Created", value=f"<t:{registered}:d>\n<t:{registered}:T>\n<t:{registered}:R>")
        customs = {"Stickers": ctx.guild.stickers, "Emojis": ctx.guild.emojis, "Roles": ctx.guild.roles}
        members = {"All": fetch_guild.approximate_member_count, "Online": fetch_guild.approximate_presence_count}
        channels = {"Text Channels": ctx.guild.text_channels, "Voice Chats": ctx.guild.voice_channels, "Forums": ctx.guild.forum_channels, "Stages": ctx.guild.stage_channels, "Categories": ctx.guild.categories, "Threads": ctx.guild.threads}
        image_limits = {"Max Emojis": ctx.guild.emoji_limit, "Max Stickers": ctx.guild.sticker_limit}
        bandwidth = {"Max Bitrate": ctx.guild.bitrate_limit, "Max Filesize": ctx.guild.filesize_limit}
        # data, method, strip if 0 or none
        to_add = {
            "Customs": [customs, len, False],
            "Members": [members, int, False],
            "Channels": [channels, len, True],
            "Image Limits": [image_limits, int, False],
            "Bandwidth": [bandwidth, Utils.convert_size, False],
        }
        for name, data in to_add.items():
            self.add_count_field(e, name, data)
        features = {}
        for feature in ctx.guild.features:
            if feature in self.ctx.discord_experiments:
                features[feature] = self.ctx.discord_experiments[feature]
            else:
                features[feature] = "Couldn't get meaning"
        if len(features) > 0:
            features_string = ""
            for id, name in sorted(features.items()):
                features_string += f"\nID: {id}\nMEANING: {name}\n"
            urls = await Utils.post(features_string)
            if urls:
                c = 0
                if len(urls) > 1:
                    for url in urls:
                        c += 1
                        e.add_field(name=f"Features Part {c}", value=f"[Click here to view]({str(url)})")
                else:
                    e.url = str(urls[0])
                    e.description = "**Click the server name to view all features**\n" + e.description
            else:
                e.description = "**Something went wrong while uploading to [rentry](https://rentry.co/)/[hastebin](https://hastebin.com/)**\n" + e.description
        e.set_footer(text=f"Server ID: {ctx.guild.id} ¤ Language {ctx.guild.preferred_locale if ctx.guild.preferred_locale is not None else 'Not Specified'}")
        await ctx.respond(embed=e)

    def add_count_field(self, e, name, data):
        string = ""
        for type, amount in sorted(data[0].items()):
            amount = data[1](amount)
            if amount != 0 and amount is not None or not data[2]:
                string += f"{amount} {type}\n"
        e.add_field(name=name, value=string)

    @bridge.bridge_command(name="userinfo", aliases=["ui", "uid", "whois", "who"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def userinfo(self, ctx, user: Optional[discord.Member]):
        """Shows you information about users"""
        user = user or ctx.author
        date_registered = Utils.iso8601_to_epoch(user.created_at.isoformat())
        e = discord.Embed(color=0xdfa3ff, description=user.mention)
        try:
            e.set_author(name=str(user), icon_url=user.avatar.url)
            e.set_thumbnail(url=user.avatar.url)
        except:
            e.set_author(name=f"{str(user)} - Couldn't get avatar")
        e.add_field(
            name="Registered",
            value=f"<t:{date_registered}:d>\n<t:{date_registered}:T>\n(<t:{date_registered}:R>)", inline=True)
        if isinstance(ctx.channel.type, discord.DMChannel) == False:
            try:
                date_joined = Utils.iso8601_to_epoch(user.joined_at.isoformat())
                members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
                e.add_field(name="Joined", value=f"<t:{date_joined}:d>\n<t:{date_joined}:T>\n(<t:{date_joined}:R>)", inline=True)
                e.add_field(name="Join position", value="This user created the server." if members.index(user) == 0 else str(members.index(user)+1), inline=True)
                if len(user.roles) > 1:
                    role_string = ' '.join(reversed([r.mention for r in user.roles][1:]))
                    if len(role_string) < 1024:
                        e.add_field(name=f"Roles [{len(user.roles)-1}]", value=role_string, inline=True)
                    else:
                        e.add_field(name=f"Roles [{len(user.roles)-1}]", value="Too many roles, can't display", inline=True)
                remove_default = ["priority_speaker", "create_instant_invite", "add_reactions", "stream", "view_channel", "send_messages", "send_tts_messages", "embed_links", "attach_files", "read_message_history", "external_emojis", "connect", "speak", "use_voice_activation", "change_nickname", "use_slash_commands", "request_to_speak", "create_public_threads", "create_private_threads", "external_stickers", "send_messages_in_threads", "start_embedded_activities"]
                perm_string = ', '.join(sorted([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1] and p[0] not in remove_default]))
                if perm_string:
                    e.add_field(name="Guild permissions", value=perm_string, inline=True)
                e.set_footer(text='ID: ' + str(user.id))
            except:
                pass
        await ctx.respond(embed=e)

    @bridge.bridge_command(name="infochannel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def infochannel(self, ctx, channel: discord.TextChannel):
        """Makes the channel you add a channel with server information"""
        try:
            if str(channel.id) in self.ctx.settings[str(ctx.guild.id)]['infochannel']:
                msg = await channel.fetch_message(int(self.ctx.settings[str(ctx.guild.id)]['infochannel'][str(channel.id)]))
                await msg.delete()
                self.ctx.settings[str(ctx.guild.id)]['infochannel'].pop(str(channel.id))
                await ctx.respond(f"Removed {channel.mention} from informational channels list")
            else:
                msg = await channel.send("_ _")
                await msg.pin()
                self.ctx.settings[str(ctx.guild.id)]['infochannel'][str(channel.id)] = str(msg.id)
                await ctx.respond(f"Added {channel.mention} to informational channels list")
            Configs.save(self.ctx.settings_path, "w", self.ctx.settings)
        except:
            await Utils.send_error(ctx, "Something went wrong, please check if I have permissions to chat, delete and pin messages in that channel.")

    @bridge.bridge_command(name="pfp")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pfp(self, ctx, user: Optional[discord.Member]):
        """Shows you the profile picture of a user"""
        user = user or ctx.author
        e = discord.Embed(color=0xdfa3ff, description=f'{user.mention} - [Link to profile picture]({user.avatar.url})')
        e.set_image(url=user.avatar.url)
        await ctx.respond(embed=e)

    @bridge.bridge_command(name="ping")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        """Tells you the bot's ping."""
        inb4 = Utils.current_milli_time()
        await Utils.delete_command_message(ctx, 11)
        e = discord.Embed(description="Pong!")
        e.set_image(url="https://c.tenor.com/LqNPvLVdzHoAAAAC/cat-ping.gif")
        message = await ctx.respond(embed=e, delete_after=10)
        inb4 = (Utils.current_milli_time() - inb4)
        e.description = f"Pong! | Command: `{inb4}ms` | Latency: `{round(self.ctx.latency * 1000)}ms`"
        await Utils.edit_message(ctx, message, embed=e)

    @bridge.bridge_command(name="botversion", aliases=["botver", "bv"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def botversion(self, ctx):
        """Tells you the bot's version."""
        await ctx.respond(f"Pycord: {discord.__version__}\nRaw data\n```\nMajor: {discord.version_info.major}, Minor: {discord.version_info.minor}, Micro: {discord.version_info.micro}\nRelease: {discord.version_info.releaselevel}\nSerial: {discord.version_info.serial}```")

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
        if await Utils.CheckInstance(ctx):
            try:
                await paginator.send(ctx, target=ctx.author)
                await ctx.reply("Check your DMs!", mention_author=False)
            except:
                await Utils.send_error(ctx, "I couldn't DM you!")
        else:
            await paginator.respond(ctx.interaction, ephemeral=True)

    @commands.command(hidden=True, name="adminstall")
    @commands.is_owner()
    @commands.guild_only()
    async def adminstall(self, ctx, option=None):
        """Shows you guides on how to install Northstar."""
        e = [self.get_pages_help()[0],
             self.get_pages_manual()[0],
             self.get_pages_automatic()[0],
             discord.Embed(description=f"{ctx.author.mention} just updated the installation embeds in <#922662496588943430>")]
        if option is not None:
            await ctx.respond(embed=e[3])
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
