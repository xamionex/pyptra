import re
import discord
from discord.ext import commands, bridge
import aiohttp
import requests
from cogs.utils import Utils as utils


def setup(bot):
    bot.add_cog(SteamCommands(bot))


class SteamCommands(commands.Cog, name="Steam Commands"):
    """Steam commands, information about games."""
    COG_EMOJI = "♨️"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(name="game", aliases=["gameinfo", "gamesearch"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def gameinfo(self, ctx, *, game):
        """Convert game name to ID"""
        message = await ctx.reply("Contacting Steam API")
        gamedata = await Utils.gametoid(game)
        game = gamedata[0]
        other = gamedata[1]
        e = discord.Embed()
        e.set_footer(text=f"Hint: use the \"{self.ctx.settings[str(ctx.guild.id)]['prefix']}gamenews\" command for the latest news from the game")
        e.color = 0x42a6cc
        if not game:
            await Utils.search_results(e, other, message)
            return
        e.title = str(game[1])
        e.url = f"https://s.team/a/{str(game[0])}"
        e.add_field(name="AppID", value=str(game[0]), inline=True)
        e.add_field(name="Open in SteamDB", value=f"[Open Link](https://steamdb.info/app/{str(game[0])})", inline=True)
        e.add_field(name="Open in Steam Client", value=f"steam://store/{str(game[0])}", inline=True)
        await message.edit("Info Found!", embed=e)

    @commands.command(name="news", aliases=["gamenews"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def gamenews(self, ctx, *, game):
        """Get the Latest news for a game"""
        try:
            message = await ctx.author.send("Contacting Steam API")
            messagedm = True
        except:
            message = await ctx.reply("Contacting Steam API")
            messagedm = False
        finally:
            gamedata = await Utils.gametoid(game)
            game = gamedata[0]
            other = gamedata[1]
            e = discord.Embed()
            e.color = 0x42a6cc
            if not game:
                await Utils.search_results(e, other, message)
                return
            news = requests.get("https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?count=1&appid=" + str(game[0]))
            try:
                news = news.json()['appnews']['newsitems'][0]
                author = news['author']
                e.title = news['title']
                e.url = news['url']
                e.color = 0x1d3a89
                e.add_field(name="Posted On", value=f"<t:{news['date']}:F> (<t:{news['date']}:R>)", inline=False)
                if author:
                    e.set_footer(text=f"Written/Posted by {author}")
                if messagedm:
                    content = news['contents']
                    if len(content) > 4096:
                        e.description = "Too big to display."
                    else:
                        e.description = news['contents']
                    await message.edit("Info Found!", embed=e)
                else:
                    await message.edit("Info Found! Couldn't send in DM. Contents removed", embed=e)
            except:
                await message.edit("No news found")


class Utils:
    async def vanitytosteamid(vanityurl):
        """Convert a vanity url to SteamID64"""
        session = aiohttp.ClientSession()
        async with session.get("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=FF0EEF99E5BD63F29FC0F938A56F115C&vanityurl=" + vanityurl) as r:
            resjson = await r.json()
        if resjson['response']['success'] != 1:
            await session.close()
            return False
        await session.close()
        return resjson['response']['steamid']

    async def search_results(e, games, message):
        e.title = "Search Results"
        if len(games.items()) > 6:
            e = await Utils.add_url(e, games)
            e.description = "If you still can't find your game try searching for it's [id here](https://steamdb.info/search/)"
            await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
            return
        elif len(games.items()) > 1:
            for appid, title in games.items():
                e.add_field(name=appid, value=f"{title}\nClient: steam://store/{str(appid)}\n[[Browser]](https://s.team/a/{str(appid)}) - [[SteamDB]](https://steamdb.info/app/{str(appid)})")
            e.description = "If you still can't find your game try searching for it's [id here](https://steamdb.info/search/)"
            await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
            return
        elif len(games.items()) == 1:
            for appid, title in games.items():
                e.title = str(title)
                e.url = f"https://s.team/a/{str(appid)}"
                e.add_field(name="AppID", value=str(appid), inline=True)
                e.add_field(name="Open in SteamDB", value=f"[Open Link](https://steamdb.info/app/{str(appid)})", inline=True)
                e.add_field(name="Open in Steam Client", value=f"steam://store/{str(appid)}", inline=True)
            e.description = "If you still can't find your game try searching for it's [id here](https://steamdb.info/search/)"
            await message.edit("I coudn't find what you were looking for, but I found this", embed=e)
            return
        else:
            await message.edit("I couldn't find what you were looking for, try searching for it's id here: <https://steamdb.info/search/>")
            return

    async def add_url(e, games):
        content = "\n"
        for appid, title in games.items():
            content = content + f"ID: `{appid}`\nTITLE: `{title}`\n\n"
        url = "https://hastebin.com/raw/"
        keys = await utils.post(content)
        c = 0
        if len(keys) > 1:
            for key in keys:
                c += 1
                e.add_field(name=f"Part {c}", value=f"[Search Results]({url + str(key)})")
        else:
            e.url = f"{url + str(keys[0])}"
        return e

    def setgame(item):
        gameid = item['appid']
        gamename = item['name']
        return gameid, gamename

    async def gametoid(game):
        """Convert a game name to its ID"""
        session = aiohttp.ClientSession()
        async with session.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/") as r:
            response = await r.json()
        gamedata = False
        othergames = {}
        for item in response['applist']['apps']:
            gameint = ''.join(re.findall('\d+', game))
            if item['appid'] == gameint and gameint == game:
                gamedata = Utils.setgame(item)
                break
            elif re.search(game, item['name'], re.IGNORECASE):
                temp = Utils.setgame(item)
                othergames[temp[0]] = temp[1]
                if str(item['name']).casefold() == str(game).casefold():
                    gamedata = Utils.setgame(item)
                    break
        await session.close()
        return gamedata, othergames

    async def idtogame(gameid):
        """Convert game ID to game name"""
        session = aiohttp.ClientSession()
        async with session.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/") as r:
            response = await r.json()
        response = response['applist']['apps']
        try:
            gamename = next((item for item in response if item["appid"] == gameid))
        except StopIteration:
            await session.close()
            return False
        gamename = gamename['name']
        await session.close()
        return gamename
