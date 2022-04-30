import json
import discord
from discord.ext import bridge

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


async def sendembed(ctx, e, show_all=True, delete=True, delete_speed=20):
    if await CheckInstance(ctx):  # checks command instance
        if delete:
            await ctx.message.delete(delay=delete_speed)
            await ctx.respond(embed=e, delete_after=delete_speed, mention_author=False)
            # if prefix and delete=true sends embed and deletes after a bit
        else:
            await ctx.message.delete(delay=delete_speed)
            await ctx.respond(embed=e, delete_after=delete_speed, mention_author=False)
            # if prefix and delete=false sends embed
    else:
        if show_all:
            await ctx.respond(embed=e)
            # if slash only and shows=true shows to all
        else:
            await ctx.respond(embed=e, ephemeral=True)
            # if slash only and shows=false only shows to user
