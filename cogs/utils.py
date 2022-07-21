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

    async def send_embed(ctx, e, ephemeral=True, mention_author=True):
        [await ctx.respond(embed=e, mention_author=mention_author) if await Utils.CheckInstance(ctx) else await ctx.respond(embed=e, ephemeral=ephemeral)]

    async def send_message(ctx, text, ephemeral=True, mention_author=False):
        [await ctx.respond(text, mention_author=mention_author) if await Utils.CheckInstance(ctx) else await ctx.respond(text, ephemeral=ephemeral)]

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
        ('w', 6.048e+8),  # 60 * 60 * 24 * 7
        ('d', 8.64e+7),   # 60 * 60 * 24
        ('h', 3.6e+6),    # 60 * 60
        ('m', 60000),
        ('s', 1000),
        ('ms', 1),
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
        (' weeks', 604800),  # 60 * 60 * 24 * 7
        (' days', 86400),    # 60 * 60 * 24
        (' hours', 3600),    # 60 * 60
        (' minutes', 60),
        (' seconds', 1),
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
