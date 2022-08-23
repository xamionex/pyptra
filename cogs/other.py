import datetime
import re
import random
import discord
from discord.ext import commands, bridge
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(OtherCommands(bot))


class OtherCommands(commands.Cog, name="Other Commands"):
    """Uncategorized commands with general use."""
    COG_EMOJI = "❔"

    def __init__(self, ctx):
        self.ctx = ctx

    @bridge.bridge_command(name="random", aliases=["rand", "choose", "pick", "roll"])
    @commands.cooldown(60, 1, commands.BucketType.user)
    async def random(self, ctx, *, choices: str):
        """Splits your message with `|` and makes a random choice."""
        choices = choices.split("|")
        if len(choices) <= 1:
            await Utils.send_error(ctx, "Please specify 2 or more choices\nExample: this | that")
        e = discord.Embed(title="I rolled 100 times")
        rolls = {}
        last = ("", 0)
        for pick in sorted(random.choices(choices, k=100)):
            try:
                rolls[pick] += 1
            except:
                rolls[pick] = 1
            if rolls[pick] > last[1]:
                last = (pick, rolls[pick])
        e.description = f"The most rolled was {last[0]} with {last[1]}%"
        for roll, percent in rolls.items():
            e.add_field(name=roll, value=f"{percent}%")
        await ctx.respond(embed=e, ephemeral=True)

    @bridge.bridge_command(hidden=True, name="echo")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def echo(self, ctx, *, message):
        """Echoes the message you send."""
        if await Utils.CheckInstance(ctx):
            await Utils.delete_command_message(ctx)
            await ctx.send(message)
        else:
            msg = await ctx.respond("Sending...", ephemeral=True)
            await ctx.send(message)
            await Utils.edit_message(ctx, msg, "Sent!")

    @bridge.bridge_command(name="poll")
    @commands.cooldown(60, 1, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def poll(self, ctx, title: str, option1: str = None, option2: str = None, option3: str = None, option4: str = None, option5: str = None, option6: str = None, option7: str = None, option8: str = None, option9: str = None, option10: str = None):
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
        if len(reactions) < 2:
            await Utils.send_error(ctx, "There needs to be 2 or more choices.")
        if not await Utils.CheckInstance(ctx):
            await ctx.respond("Sent!", ephemeral=True)
        msg = await ctx.send(embed=e)
        for reaction in reactions:
            await msg.add_reaction(reaction)

    @bridge.bridge_command(hidden=True, name="free")
    @commands.is_owner()
    async def free(self, ctx, title: str, description: str, price: str, how_long: str, rating: str, platform: str, game_link: str, image_link: str):
        """Sends a freestuff bot-like embed (can be used by petar only)."""
        unix = Utils.time_from_string_in_seconds(how_long)[0] + Utils.current_time()
        await Utils.delete_command_message(ctx)
        platforms = {
            "gog": "https://cdn.discordapp.com/attachments/764940369367662622/989443585533440020/unknown.png",
            "epic": "https://cdn.discordapp.com/attachments/764940369367662622/989443614130192474/unknown.png",
            "steam": "https://cdn.discordapp.com/attachments/764940369367662622/989443638989828136/unknown.png",
            "itchio": "https://cdn.discordapp.com/attachments/764940369367662622/989443462673883156/unknown.png",
            "battle.net": "https://cdn.discordapp.com/attachments/764940369367662622/1011466963937140756/unknown.png"
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
        e.set_image(url=image_link)
        e.set_footer(text=f"Sent from {ctx.author}")
        # channel = self.ctx.get_channel(935685344010047519)
        await ctx.send(embed=e)

    @bridge.bridge_command(name="unix")
    async def unix(self, ctx, time):
        """Takes any time you put in (1d 2h 3m 4s...) and makes it into unix"""
        unix = Utils.time_from_string_in_seconds(time)[0] + Utils.current_time()
        await Utils.delete_command_message(ctx, 20)
        await ctx.respond(embed=discord.Embed(title="That comes up to", description=unix), ephemeral=True, delete_after=20)

    @commands.command(hidden=True, name="echoembed")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def echoembed(self, ctx, description):
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
    async def reply(self, ctx, *, message):
        """Reply to someone's message with this command, It'll reply with the bot"""
        reference = ctx.message.reference
        if reference is None:
            await Utils.send_error(ctx, f"You didn't reply to any message.")
        await reference.resolved.reply(message)
        await Utils.delete_command_message(ctx)

    @commands.slash_command(hidden=True, name="reply")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def slash_reply(self, ctx, message_id, *, message):
        """Reply to someone's message with this command, It'll reply with the bot"""
        smsg = await ctx.respond("Sending...", ephemeral=True)
        message_id = int(re.findall("\d+", message_id)[0])
        try:
            msg = await ctx.fetch_message(message_id)
            await msg.reply(message)
        except:
            await Utils.send_error(ctx, "Couldn't reply to message")
        await Utils.edit_message(ctx, smsg, "Sent!")

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
