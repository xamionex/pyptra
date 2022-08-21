import http.cookiejar
import urllib.parse
from json import loads as json_loads
from http.cookies import SimpleCookie
import urllib.request
import math
import unicodedata
import time
import aiohttp
import calendar
from datetime import datetime
import re
import discord
from discord.ext import bridge, commands


def setup(bot):
    bot.add_cog(Utils(bot))


MISSING: object() = discord.utils.MISSING


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

    async def delete_command_message(ctx, delete_speed=None):
        try:
            if delete_speed is None:
                await ctx.message.delete()
            else:
                await ctx.message.delete(delay=delete_speed)
        except:
            return

    async def edit_message(ctx, message, text: str = MISSING, embed=MISSING, file=MISSING):
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

    def display_time(milliseconds, granularity=None):
        result = []
        for name, count in Utils.intervals_milliseconds:
            value = round(milliseconds // count)
            if value:
                milliseconds -= value * count
                result.append(f"{int(value)}{name}")
        return ', '.join(result[:granularity]) if granularity is not None else ', '.join(result)

    intervals_seconds = (
        (' years', 3.154e+7),   # * 12
        (' months', 2.628e+6),  # * 4.34524
        (' weeks', 604800),     # * 7
        (' days', 86400),       # * 24
        (' hours', 3600),       # * 60
        (' minutes', 60),       # * 60
        (' seconds', 1),        # * 1
    )

    def display_time_s(seconds, granularity=None):
        result = []
        for name, count in Utils.intervals_seconds:
            value = round(seconds // count)
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append(f"{value}{name}")
        return ', '.join(result[:granularity]) if granularity is not None else ', '.join(result)

    def current_milli_time():
        return round(time.time() * 1000)

    def current_time():
        return round(time.time())

    def time_from_string_in_seconds(text):
        time = re.match(r"^(([0-9])+(y(ear)?|mo(nth)?|w(eek)?|d(ay)?|h(our)?|m(in)?(ute)?|s(econd)?)?s? ?)+", text, re.IGNORECASE)[0]
        text = text.replace(time, "")
        time = time.replace(" ", "")
        time_list = {
            r"y": 3.154e+7,   # * 12
            r"mo": 2.628e+6,  # * 4.34524
            r"w": 604800,     # * 7
            r"d": 86400,      # * 24
            r"h": 3600,       # * 60
            r"m(?!o)": 60,    # * 60
            r"s": 1           # * 1
        }
        seconds = 0
        for pattern in time_list:
            result = 0
            for catch in re.findall(fr"[0-9]+{pattern}", time, re.IGNORECASE):
                result += int(re.search("\d+", catch)[0])
            seconds += result * time_list[pattern] if result > 0 else 0
        if seconds == 0 and time.isalnum():
            seconds = int(time)
        return round(int(seconds)), text

    def strip_accents(text):
        try:
            text = str(text, 'utf-8')
        except:  # unicode is a default on python 3
            pass
        return str(unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8"))

    def convert_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    async def post(text, domain="rentry"):
        split_strings = [text[i:i+200000] for i in range(0, len(text), 200000)]
        urls = []
        domain = "rentry" if domain == "rentry" and urllib.request.urlopen("https://rentry.co/api/new").getcode() == 200 or len(split_strings) < 2 else "hastebin" if urllib.request.urlopen("https://hastebin.com/documents").getcode() == 200 else False
        if not domain:
            return False
        if domain == "hastebin":
            for string in split_strings:
                async with aiohttp.ClientSession() as session:
                    async with session.post("https://hastebin.com/documents", data=string.encode('utf-8')) as post:
                        post = await post.json()
                        urls.append(post['key'])
            for key in urls:
                key = f"https://hastebin.com/{key}"
        else:
            for string in split_strings:
                client, cookie = Utils.UrllibClient(), SimpleCookie()
                cookie.load(vars(client.get('https://rentry.co'))['headers']['Set-Cookie'])
                csrftoken = cookie['csrftoken'].value
                payload = {
                    'csrfmiddlewaretoken': csrftoken,
                    'text': string
                }

                urls.append(json_loads(client.post('https://rentry.co/api/new', payload, headers={"Referer": 'https://rentry.co'}).data)['url'])
        return urls

    class UrllibClient:
        """Simple HTTP Session Client, keeps cookies."""

        def __init__(self):
            self.cookie_jar = http.cookiejar.CookieJar()
            self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
            urllib.request.install_opener(self.opener)

        def get(self, url, headers={}):
            request = urllib.request.Request(url, headers=headers)
            return self._request(request)

        def post(self, url, data=None, headers={}):
            postdata = urllib.parse.urlencode(data).encode()
            request = urllib.request.Request(url, postdata, headers)
            return self._request(request)

        def _request(self, request):
            response = self.opener.open(request)
            response.status_code = response.getcode()
            response.data = response.read().decode('utf-8')
            return response
