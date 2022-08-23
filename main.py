import json
import os
import discord
#import asyncio
#import random
from discord.ext import commands, bridge  # , tasks
# cogs
import secrets
from cogs import block
from cogs.utils import Utils

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True


def get_prefix(bot, msg):
    with open("./data/settings.json", "r") as f:
        prefixes = json.load(f)
        try:
            prefix = prefixes[str(msg.guild.id)]["prefix"]
        except:
            prefix = "-"
    return prefix


def when_mentioned_or_function(func):
    def inner(bot, msg):
        r = commands.when_mentioned(bot, msg)
        r.append(func(bot, msg))
        return r
    return inner


bot = bridge.Bot(
    command_prefix=when_mentioned_or_function(get_prefix),
    intents=intents,
    allowed_mentions=discord.AllowedMentions(
        everyone=False,      # Whether to ping @everyone or @here mentions
        roles=False,         # Whether to ping role @mentions
    ),
)


@bot.before_invoke
async def on_command(ctx):
    try:
        if ctx.author.guild_permissions.administrator:
            ctx.command.reset_cooldown(ctx)
        if bot.settings[str(ctx.guild.id)]["perms"][str(ctx.author.id)]['blacklist'] and not ctx.author.guild_permissions.administrator:
            await Utils.send_error(ctx, f"You were **blocked** from using this bot, direct message a moderator if you feel this is unfair")
    except KeyError:
        pass

"""@tasks.loop(minutes=random.randrange(0, 10, 1), count=3)
async def spam_terror():
    channel = bot.get_channel(
        947548676870524968)  # Get the channel, the id has to be an int
    await channel.send('Message to update last message timestamp (Discord allows you to see that without seeing the channel for some reason)', delete_after=60)


@spam_terror.before_loop
async def spam_terror_before_loop():
    await bot.wait_until_ready()


@spam_terror.after_loop
async def spam_terror_after_loop():
    await asyncio.sleep(random.randrange(1800, 3600, 200))
    spam_terror.start()"""


@bot.event
async def on_message(message):
    # remove markdown
    message.content = Utils.escape_markdown(message.content)
    for x, v in {"french": "fr\*nch", "france": "fr\*nce"}.items():
        message.content = message.content.replace(x, v)
    # stop if user is bot or is mentioning @everyone
    if message.mention_everyone or message.author.bot:
        return


def extensions():
    extensions = []
    skip = ["suggestions"]
    for module in next(os.walk("cogs"), (None, None, []))[2]:  # [] if no file
        module = module.replace('.py', '')
        if module not in skip:
            extensions.append(module)
    bot.extensions_list, bot.skip_list = extensions, skip
    return extensions


for module in extensions():
    bot.load_extension(f"cogs.{module}")
print("Found", end=" ")
print(*bot.extensions_list, sep=', ')
print("Ignored", end=" ")
print(*bot.skip_list, sep=', ')
# spam_terror.start()
bot.run(secrets.secret)
