import re
import discord
from discord.ext import commands, bridge
import aiohttp
import asyncio
import async_timeout
import requests
import time
from cogs import utils


def setup(bot):
    bot.add_cog(SteamCommands(bot))


class SteamCommands(commands.Cog, name="Steam Commands"):
    """Steam commands, information about games."""
    COG_EMOJI = "👤"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command()
    async def gameinfo(self, ctx, *, gamename):
        """Convert game name to ID"""
        message = await ctx.send("Contacting Steam API", delete_after=30)
        game = await Utils.gametoid(gamename)
        if not game:
            await message.delete()
            await utils.senderror(ctx, "I couldn't find what you were looking for, try searching for it's [id here](https://steamdb.info/search/).")
        embed = discord.Embed(title="Steam Game Information", url="https://store.steampowered.com/app/" + str(game[0]),
                              description="Info for Requested Game", color=0x42a6cc)
        embed.add_field(name="Steam Game ID", value=game[0], inline=True)
        embed.add_field(name="Steam Game Name", value=game[1], inline=True)
        embed.set_footer(
            text="Hint: use the \"gamenews\" command for the latest news from the game")
        await message.edit("Info Found!", embed=embed)

    @commands.command()
    async def gamenews(self, ctx, *, game):
        """Get the Latest news for a game"""
        try:
            message = await ctx.author.send("Contacting Steam API")
            messagedm = True
        except:
            message = await ctx.send("Contacting Steam API", delete_after=30)
            messagedm = False
        finally:
            game = await Utils.gametoid(game)
            if not game:
                await message.delete()
                await utils.senderror(ctx, "I couldn't find what you were looking for, try searching for it's [id here](https://steamdb.info/search/).")
            news = requests.get("https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?count=1&appid=" + str(game[0]))
            print(f"Check: {game[0]} - {game[1]}")
            try:
                news = news.json()['appnews']['newsitems'][0]
                author = news['author']
                e = discord.Embed(title=news['title'], url=news['url'], color=0x1d3a89)
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
        try:
            for item in response['applist']['apps']:
                try:
                    if item['appid'] == int(''.join(re.findall('\d+', game))):
                        gamedata = Utils.setgame(item)
                        break
                except:
                    if item['name'].casefold() == game.casefold():
                        gamedata = Utils.setgame(item)
                        break
        except:
            pass
        await session.close()
        return gamedata

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
