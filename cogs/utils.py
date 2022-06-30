import aiohttp
import calendar
from datetime import datetime
import json
import os
import re
import discord
from discord.ext import bridge, commands

bot: discord.Bot = None

channelMap = {
    941433221093130270:
    {
        "mods": 951269271990837278,
        "server": 952003821004017754
    },
    920776187884732556:
    {
        "mods": 951255789568409600,
        "server": 952007443842469928
    },
    196573388423168000:
    {
        "mods": 967199137252642876,
        "server": 967199174485479485
    }
}

datasets = {
    "mods": {},
    "server": {}
}
with open("./data/suggestions_mods.json", "r") as f:
    datasets["mods"] = json.load(f)
with open("./data/suggestions_server.json", "r") as f:
    datasets["server"] = json.load(f)

# TODO: should probably use classes or smth for this mess


def formatEmbed(data: dict, domain):
    color = discord.Color(0xe5da10)
    user = bot.get_user(data["user"])
    status = data["status"]
    sid = data["sid"]
    suggestion = data["suggestion"]
    if status == "approved":
        color = discord.Color(0x21ba24)
    elif status == "denied":
        color = discord.Color(0xc9261e)
    embed = discord.Embed(
        title=f"Suggestion #{sid}", description="", color=color)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Submitter", value=user.mention, inline=False)
    embed.add_field(name="Suggestion", value=suggestion, inline=False)
    embed.add_field(name="Status", value=status, inline=False)
    if data["note"] != "":
        embed.add_field(name="Staff note", value=data["note"], inline=False)
    embed.set_footer(text=f"ID: {sid}")
    return embed


def addSuggestion(userid: int, suggestion: str, domain: str):
    datasets[domain]["latestId"] += 1
    datasets[domain]["suggestions"].append({
        "user": userid,
        "suggestion": suggestion,
        "sid": datasets[domain]["latestId"],
        "message": 0,
        "status": "open",
        "note": ""
    })
    return datasets[domain]["suggestions"][datasets[domain]["latestId"]]


def saveData():
    with open("./data/suggestions_mods.json", "w") as f1:
        json.dump(datasets["mods"], f1, indent=4)
    with open("./data/suggestions_server.json", "w") as f2:
        json.dump(datasets["server"], f2, indent=4)


def setSuggestionState(ctx: discord.ApplicationContext, sid: int, state: str, domain: str):
    if ctx.author.guild_permissions.administrator:
        sidList = [entry["sid"] for entry in datasets[domain]["suggestions"]]
        if sid in sidList:
            data = datasets[domain]["suggestions"][sid]
            datasets[domain]["suggestions"][sid]["status"] = state
            saveData()
            return True
        else:
            return False


async def suggestion_internal(ctx: discord.ApplicationContext, suggestion: discord.Option(str, "suggestion"), domain: str):
    target_channel = 0
    if ctx.guild_id in channelMap:
        target_channel = channelMap[ctx.guild_id][domain]
    if target_channel != 0:
        print(target_channel)
        suggestionObj = addSuggestion(ctx.author.id, suggestion, domain)
        interaction: discord.Interaction = ctx.interaction
        embed = formatEmbed(suggestionObj, domain)
        message = await ctx.guild.get_channel(target_channel).send(embed=embed)
        datasets[domain]["suggestions"][datasets[domain]
                                        ["latestId"]]["message"] = message.id
        saveData()
        await ctx.respond("Thank you for your suggestion!", ephemeral=True)
        await message.add_reaction(":holo:923453792006049863")
        await message.add_reaction(":terror:923705791486246922")
    else:
        print("Target channel was 0")


async def approve1(ctx: discord.ApplicationContext, domain: str, sid: str):
    if setSuggestionState(ctx, int(sid), "approved", domain):
        datasets[domain]["suggestions"][int(sid)]["status"] = "approved"
        data = datasets[domain]["suggestions"][int(sid)]
        message = await ctx.guild.get_channel(channelMap[ctx.guild.id][domain]).get_partial_message(data["message"]).fetch()
        embed = formatEmbed(data, domain)
        await message.edit(embed=embed)
        await ctx.send(f"Approved suggestion {sid} in {domain}")
    else:
        await ctx.send("That ID does not exist")


async def deny1(ctx: discord.ApplicationContext, domain: str, sid: str):
    if setSuggestionState(ctx, int(sid), "denied", domain):
        datasets[domain]["suggestions"][int(sid)]["status"] = "denied"
        data = datasets[domain]["suggestions"][int(sid)]
        message = await ctx.guild.get_channel(channelMap[ctx.guild.id][domain]).get_partial_message(data["message"]).fetch()
        embed = formatEmbed(data, domain)
        await message.edit(embed=embed)
        await ctx.send(f"Denied suggestion {sid} in {domain}")
    else:
        await ctx.send("That ID does not exist")


async def addnote(ctx: discord.ApplicationContext, domain: str, sid: str, note: str):
    if ctx.author.guild_permissions.administrator:
        datasets[domain]["suggestions"][int(
            sid)]["note"] = f"{note} - {ctx.author.mention}"
        data = datasets[domain]["suggestions"][int(sid)]
        message = await ctx.guild.get_channel(channelMap[ctx.guild.id][domain]).get_partial_message(data["message"]).fetch()
        embed = formatEmbed(data, domain)
        await message.edit(embed=embed)
        await ctx.send(f"Add note to {sid} in {domain}")
    else:
        await ctx.send(f"You don't have permission to do that.")


async def ping(ctx):
    e = discord.Embed(title=f"Pong! `{round(bot.latency * 1000)}ms`")
    e.set_image(url="https://c.tenor.com/LqNPvLVdzHoAAAAC/cat-ping.gif")
    return e


async def CheckInstance(ctx):
    if isinstance(ctx, bridge.BridgeExtContext):
        return True  # prefix returns true
    elif isinstance(ctx, bridge.BridgeApplicationContext):
        return False  # slash returns false


async def sendembed(ctx, e, show_all=True, delete=1, delete_speed=5):
    if await CheckInstance(ctx):  # checks if command is slash or not
        if delete == 0:
            await ctx.respond(embed=e, mention_author=False, delete_after=delete_speed)
        elif delete == 1:
            await ctx.respond(embed=e, mention_author=False)
        elif delete == 2:
            await ctx.respond(embed=e, mention_author=False)
            await delete_message(ctx, delete_speed)
        else:
            await ctx.respond(embed=e, delete_after=delete_speed, mention_author=False)
            await delete_message(ctx, delete_speed)
            # 0 deletes bots reply, 1 doesnt delete, 2 deletes only cause, 3 deletes all
    else:
        if show_all:
            await ctx.respond(embed=e)
        else:
            await ctx.respond(embed=e, ephemeral=True)
        # true shows in chat, false shows to user only


async def senddmembed(ctx, e, delete=False, delete_speed=5):
    if delete:
        await ctx.author.send(embed=e, delete_after=delete_speed)
    else:
        await ctx.author.send(embed=e)
        # False doesnt delete, True deletes bot's msg


async def delete_message(ctx, delete_speed=None):
    try:
        if delete_speed is None:
            await ctx.message.delete()
        else:
            await ctx.message.delete(delay=delete_speed)
    except Exception:
        return


async def edit_msg(self, ctx, message, edit):
    if await CheckInstance(ctx):
        await message.edit(edit)
    else:
        await message.edit_original_message(content=edit)


async def delete_msg(self, ctx, message):
    if await CheckInstance(ctx):
        await message.delete()
    else:
        await message.delete_original_message()


async def senderror(ctx, cerror):
    #e = discord.Embed(description=cerror, color=0xFF6969)
    # await sendembed(ctx, e, False)
    if await CheckInstance(ctx):
        raise commands.CommandError(cerror)
    else:
        raise discord.ApplicationCommandError(cerror)


def extensions():
    extensions = []
    skip_list = ["utils", "suggestions"]
    for module in next(os.walk("cogs"), (None, None, []))[2]:  # [] if no file
        module = module.replace('.py', '')
        if module not in skip_list:
            extensions.append(module)
    return extensions, skip_list


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


def period(delta, pattern):
    d = {'d': delta.days}
    d['h'], rem = divmod(delta.seconds, 3600)
    d['m'], d['s'] = divmod(rem, 60)
    return pattern.format(**d)


async def post(content):
    split_strings = [content[i:i+390000] for i in range(0, len(content), 390000)]
    keys = []
    for string in split_strings:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://www.toptal.com/developers/hastebin/documents", data=string.encode('utf-8')) as post:
                post = await post.json()
                keys.append(post['key'])
    return keys
