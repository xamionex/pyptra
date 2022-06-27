import re
import discord
from discord.ext import commands, bridge
import aiohttp
import requests
from cogs import utils
import main


def setup(bot):
    bot.add_cog(SteamCommands(bot))


class SteamCommands(commands.Cog, name="Steam Commands"):
    """Steam commands, information about games."""
    COG_EMOJI = "♨️"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def gameinfo(self, ctx, *, game):
        """Convert game name to ID"""
        message = await ctx.reply("Contacting Steam API", delete_after=120)
        gamedata = await Utils.gametoid(game)
        game = gamedata[0]
        other = gamedata[1]
        e = discord.Embed()
        e.set_footer(text=f"Hint: use the \"{main.get_prefix(self.ctx, ctx.message)}gamenews\" command for the latest news from the game")
        e.color = 0x42a6cc
        if not game:
            e.title = "Search Results"
            if len(other.items()) > 5:
                content = "\n"
                for appid, title in other.items():
                    content = content + f"ID: `{appid}`\nTITLE: `{title}`\n\n"
                post = await utils.post(content)
                e.url = post
                e.description = "If you still can't find your game try searching for it's [id here](https://steamdb.info/search/)"
                await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
                return
            elif len(other.items()) > 0:
                for title, appid in other.items():
                    e.add_field(name=title, value=appid)
                e.description = "If you still can't find your game try searching for it's [id here](https://steamdb.info/search/)"
                await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
                return
            else:
                await message.delete()
                await utils.senderror(ctx, "I couldn't find what you were looking for, try searching for it's [id here](https://steamdb.info/search/).")
        e.title = str(game[1])
        e.url = f"https://s.team/a/{str(game[0])}"
        e.add_field(name="AppID", value=str(game[0]), inline=True)
        e.add_field(name="Open in SteamDB", value=f"[Open Link](https://steamdb.info/app/{str(game[0])})", inline=True)
        e.add_field(name="Open in Steam Client", value=f"steam://store/{str(game[0])}", inline=True)
        await message.edit("Info Found!", embed=e)

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def gamenews(self, ctx, *, game):
        """Get the Latest news for a game"""
        try:
            message = await ctx.author.send("Contacting Steam API")
            messagedm = True
        except:
            message = await ctx.reply("Contacting Steam API", delete_after=120)
            messagedm = False
        finally:
            gamedata = await Utils.gametoid(game)
            game = gamedata[0]
            other = gamedata[1]
            e = discord.Embed()
            e.color = 0x42a6cc
            if not game:
                e.title = "Search Results"
                if len(other.items()) > 5:
                    content = "\n"
                    for appid, title in other.items():
                        content = content + f"ID: `{appid}`\nTITLE: `{title}`\n\n"
                    post = await utils.post(content)
                    e.url = post
                    e.description = "If you still can't find your game try searching for it's [id here](https://steamdb.info/search/)"
                    await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
                    return
                elif len(other.items()) > 0:
                    for title, appid in other.items():
                        e.add_field(name=title, value=appid)
                    e.description = "If you still can't find your game try searching for it's [id here](https://steamdb.info/search/)"
                    await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
                    return
                else:
                    await message.delete()
                    await utils.senderror(ctx, "I couldn't find what you were looking for, try searching for it's [id here](https://steamdb.info/search/).")
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
                    await message.edit("Info Found! Sending full info in DM", embed=e)
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
            if item['appid'] == ''.join(re.findall('\d+', game)):
                gamedata = Utils.setgame(item)
                break
            elif re.search(game, item['name'], re.IGNORECASE):
                temp = Utils.setgame(item)
                othergames[temp[0]] = temp[1]
                if item['name'].casefold() == game.casefold():
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
