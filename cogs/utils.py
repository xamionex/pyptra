import unicodedata
import time
import aiohttp
import calendar
from datetime import datetime
import os
import re
import discord
from discord.utils import MISSING
from discord.ext import bridge, commands


def setup(bot):
    bot.add_cog(Utils(bot))


class Utils(commands.Cog, name="Utils"):
    """Utility funcs."""
    COG_EMOJI = "⚙️"

    def __init__(self, ctx):
        self.ctx = ctx

    async def CheckInstance(ctx):
        if isinstance(ctx, bridge.BridgeExtContext):
            return True  # prefix returns true
        elif isinstance(ctx, bridge.BridgeApplicationContext):
            return False  # slash returns false

    def is_reply(msg):
        # if it's a reply and not a system message return True else False
        if msg.reference is not None and not msg.is_system:
            return True
        return False

    async def send_embed(ctx, e, ephemeral=True, mention_author=True, delete_after=MISSING):
        [await ctx.respond(embed=e, mention_author=mention_author, delete_after=delete_after) if await Utils.CheckInstance(ctx) else await ctx.respond(embed=e, ephemeral=ephemeral)]

    async def send_message(ctx, text, ephemeral=True, mention_author=False, delete_after=MISSING):
        [await ctx.respond(text, mention_author=mention_author, delete_after=delete_after) if await Utils.CheckInstance(ctx) else await ctx.respond(text, ephemeral=ephemeral)]

    async def send_embed_dm(ctx, e, delete=False, delete_speed=5):
        if delete:
            await ctx.author.send(embed=e, delete_after=delete_speed)
        else:
            await ctx.author.send(embed=e)
            # False doesnt delete, True deletes bot's msg

    async def delete_command_message(ctx, delete_speed=None):
        try:
            if delete_speed is None:
                await ctx.message.delete()
            else:
                await ctx.message.delete(delay=delete_speed)
        except Exception:
            return

    async def edit_message(ctx, message, text=MISSING, embed=MISSING, file=MISSING):
        if await Utils.CheckInstance(ctx):
            await message.edit(text, embed=embed, file=file)
        else:
            await message.edit_original_message(content=text, embed=embed, file=file)

    async def delete_message(ctx, message):
        try:
            if await Utils.CheckInstance(ctx):
                await message.delete()
            else:
                await message.delete_original_message()
        except Exception:
            return

    async def send_error(ctx, error, msg=None):
        if msg is not None:
            await Utils.delete_message(ctx, msg)
        if await Utils.CheckInstance(ctx):
            raise commands.CommandError(error)
        else:
            raise discord.ApplicationCommandError(error)

    async def can_dm_user(user: discord.User) -> bool:
        ch = user.dm_channel
        if ch is None:
            ch = await user.create_dm()

        try:
            await ch.send()
        except discord.Forbidden:
            return False
        except discord.HTTPException:
            return True

    def escape_markdown(text):
        # escapes `` and \ (discord's escape character), for more chars just add them inside ([])
        parse = re.sub(r"([\\`])", r"\\\1", text)
        reparse = re.sub(r"\\\\([\\`])", r"\1", parse)
        return reparse

    def remove_newlines(text):
        new_text = " ".join(text.split())
        return new_text

    def epoch_to_iso8601(timestamp):
        """
        epoch_to_iso8601 - convert the unix epoch time into a iso8601 formatted date
        >>> epoch_to_iso8601(1341866722)
        '2012-07-09T22:45:22'
        """
        return datetime.fromtimestamp(timestamp).isoformat()

    def iso8601_to_epoch(datestring):
        """
        iso8601_to_epoch - convert the iso8601 date into the unix epoch time
        >>> iso8601_to_epoch("2012-07-09T22:27:50.272517+00:00")
        1341872870
        """
        return calendar.timegm(datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    intervals_milliseconds = (
        ('y', 6.048e+8),    # * 12
        ('mo', 6.048e+8),   # * 4.34524
        ('w', 6.048e+8),    # * 7
        ('d', 8.64e+7),     # * 24
        ('h', 3.6e+6),      # * 60
        ('m', 60000),       # * 60
        ('s', 1000),        # * 1000
        ('ms', 1),          # * 1
    )

    def display_time(milliseconds, granularity=2):
        result = []
        for name, count in Utils.intervals_milliseconds:
            value = milliseconds // count
            if value:
                milliseconds -= value * count
                result.append(f"{int(value)}{name}")
        return ', '.join(result[:granularity])

    intervals_seconds = (
        (' years', 3.154e+7),   # * 12
        (' months', 2.628e+6),  # * 4.34524
        (' weeks', 604800),     # * 7
        (' days', 86400),       # * 24
        (' hours', 3600),       # * 60
        (' minutes', 60),       # * 60
        (' seconds', 1),        # * 1
    )

    def display_time_s(seconds, granularity=2):
        result = []
        for name, count in Utils.intervals_seconds:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append(f"{int(value)}{name}")
        return ', '.join(result[:granularity])

    def current_milli_time():
        return round(time.time() * 1000)

    def current_time():
        return round(time.time())

    def time_from_string_in_seconds(text):
        time = re.match(r"^(([0-9])+(y(ear)?|month|w(eek)?|d(ay)?|h(our)?|m(inute)?|s(econd)?)?s? ?)+", text, re.IGNORECASE)[0]
        text = text.replace(time, "")
        time = time.replace(" ", "")
        time_list = {
            "y(ear)?": 3.154e+7,    # * 12
            "month": 2.628e+6,      # * 4.34524
            "w(eek)?": 604800,      # * 7
            "d(ay)?": 86400,        # * 24
            "h(our)?": 3600,        # * 60
            "m(inute)?": 60,        # * 60
            "s(econd)?": 1          # * 1
        }
        seconds = 0
        for pattern in time_list:
            match = "".join(re.findall(r"\d+", str(re.findall(rf'([0-9])+{pattern}s?', time, re.IGNORECASE))))
            match = 0 if match == "" else int(match)
            seconds += match * time_list[pattern] if match > 0 else 0
        if seconds == 0 and time.isalnum():
            seconds = int(time)
        return round(int(seconds)), text

    async def post(content):
        split_strings = [content[i:i+390000] for i in range(0, len(content), 390000)]
        keys = []
        for string in split_strings:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://www.toptal.com/developers/hastebin/documents", data=string.encode('utf-8')) as post:
                    post = await post.json()
                    keys.append(post['key'])
        return keys

    def strip_accents(text):
        try:
            text = str(text, 'utf-8')
        except:  # unicode is a default on python 3
            pass
        return str(unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8"))
