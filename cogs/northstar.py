import re
import discord
from discord.ext import commands
import aiohttp
from cogs.utils import Utils as utils
import urllib.parse


def setup(bot):
    bot.add_cog(NorthstarCommands(bot))


class NorthstarCommands(commands.Cog, name="Northstar commands"):
    """Northstar commands, information about Northstar servers."""
    COG_EMOJI = "💫"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(name="server", aliases=["serverinfo", "serversearch"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def server(self, ctx, *, server):
        """Search for a server"""
        message = await ctx.reply("Contacting Northstar API")
        gamedata = await Utils.search(server)
        game = gamedata[0]
        other = gamedata[1]
        e = discord.Embed()
        e.color = 0x42a6cc
        if not game:
            await Utils.search_results(e, other, message)
            return
        e.title = str(game[1])
        e.url = f"https://petar.tk/northstar?id={urllib.parse.quote(game[0])}&name={urllib.parse.quote(game[1])}"
        e.add_field(name="id", value=str(game[0]), inline=False)
        await message.edit("Info Found!", embed=e)


class Utils:
    async def search_results(e, games, message):
        e.title = "Search Results"
        if len(games.items()) > 6:
            e = await Utils.add_url(e, games)
            await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
            return
        elif len(games.items()) > 1:
            for id, title in games.items():
                e.add_field(name=title, value=f"[Join](https://petar.tk/northstar?id={urllib.parse.quote(id)}&name={urllib.parse.quote(title)})")
            await message.edit("I coudn't find what you were looking for, but I found these", embed=e)
            return
        elif len(games.items()) == 1:
            for id, title in games.items():
                e.title = str(title)
                e.url = f"https://petar.tk/northstar?id={urllib.parse.quote(id)}&name={urllib.parse.quote(title)}"
            await message.edit("I coudn't find what you were looking for, but I found this", embed=e)
            return
        else:
            await message.edit("I couldn't find what you were looking for")
            return

    async def add_url(e, games):
        content = "\n"
        for id, title in games.items():
            content = content + f"ID: `{id}`\nTITLE: `{title}`\n\n"
        url = "https://www.toptal.com/developers/hastebin/raw/"
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
        gameid = item['id']
        gamename = item['name']
        return gameid, gamename

    async def search(game):
        """Convert a game name to its ID"""
        session = aiohttp.ClientSession()
        async with session.get("https://northstar.tf/client/servers") as r:
            response = await r.json()
        gamedata = False
        othergames = {}
        for item in response:
            gm = ''.join(game.split(" "))
            if item['id'] == gm:
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
