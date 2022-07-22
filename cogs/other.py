import datetime
import discord
from discord.ext import commands
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(OtherCommands(bot))


class OtherCommands(commands.Cog, name="Other Commands"):
    """Uncategorized commands with general use."""
    COG_EMOJI = "❔"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(hidden=True, name="echo")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def echo(self, ctx, *, message=None):
        """Echoes the message you send."""
        await Utils.delete_command_message(ctx)
        await ctx.send(message)

    @commands.command(name="poll")
    @commands.cooldown(60, 1, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def poll(self, ctx, title: str, option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None, option6: str = None, option7: str = None, option8: str = None, option9: str = None, option10: str = None):
        """Makes a poll with your choices."""
        await Utils.delete_command_message(ctx)
        e = discord.Embed(description=f"**{title}**\n", timestamp=datetime.datetime.now())
        e.set_footer(text=f"Poll by {ctx.author}")
        options = {
            "1️⃣": option1,
            "2️⃣": option2,
            "3️⃣": option3,
            "4️⃣": option4,
            "5️⃣": option5,
            "6️⃣": option6,
            "7️⃣": option7,
            "8️⃣": option8,
            "9️⃣": option9,
            "🔟": option10
        }
        reactions = []
        for number, choice in options.items():
            if choice is not None:
                choice = Utils.remove_newlines(choice)
                e.description = e.description + f"\n{number} {str(choice)}"
                reactions.append(number)
        msg = await ctx.send(embed=e)
        for reaction in reactions:
            await msg.add_reaction(reaction)

    @commands.command(hidden=True, name="free")
    @commands.is_owner()
    @commands.guild_only()
    async def free(self, ctx, title, description, price, unix, rating, platform, game_link, imagelink):
        """Sends a freestuff bot-like embed (can be used by petar only)."""
        await Utils.delete_command_message(ctx)
        platforms = {
            "gog": "https://cdn.discordapp.com/attachments/764940369367662622/989443585533440020/unknown.png",
            "epic": "https://cdn.discordapp.com/attachments/764940369367662622/989443614130192474/unknown.png",
            "steam": "https://cdn.discordapp.com/attachments/764940369367662622/989443638989828136/unknown.png",
            "itchio": "https://cdn.discordapp.com/attachments/764940369367662622/989443462673883156/unknown.png",
        }
        for name, link in platforms.items():
            if str(platform) == str(name):
                platform = str(link)
                break
        e = discord.Embed(
            title=title, description=f"""
            > {description}\n
            ~~€{price}~~ **Free** until <t:{unix}:d> ᲼ ᲼ {rating} ★\n
            **[Get it for free]({game_link})**
            """)
        e.set_thumbnail(url=platform)
        e.set_image(url=imagelink)
        e.set_footer(text=f"Sent from {ctx.author}")
        # channel = self.ctx.get_channel(935685344010047519)
        await ctx.send(embed=e)

    @commands.command(hidden=True, name="echoembed")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def echoembed(self, ctx, description=None):
        """Echos the message you put in with an embed."""
        await Utils.delete_command_message(ctx)
        if description is None:
            await Utils.send_error(ctx, "No message attached")
        e = discord.Embed(description=description)
        # channel = self.ctx.get_channel(935685344010047519)
        await ctx.send(embed=e)

    @commands.command(hidden=True, name="reply")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def reply(self, ctx, *, message=None):
        """Reply to someone's message with this command, It'll reply with the bot"""
        reference = ctx.message.reference
        if reference is None:
            await Utils.send_error(ctx, f"You didn't reply to any message.")
        await reference.resolved.reply(message)
        await Utils.delete_command_message(ctx)

    @commands.command(hidden=True, name="dm")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def dm(self, ctx, user: discord.User, *, message):
        """DM someone without the message saying your name"""
        await user.send(embed=discord.Embed(title=f"Sent from {ctx.guild.name}", description=message))
        await Utils.delete_command_message(ctx)

    @commands.command(hidden=True, name="nick")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def nick(self, ctx, member: discord.Member, *, nick):
        """Changes a users nickname"""
        await member.edit(nick=nick)
        await Utils.delete_command_message(ctx)
