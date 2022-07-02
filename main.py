import asyncio
import json
import discord
import random
from discord.ext import commands, bridge, tasks
# cogs
import secrets
from cogs import block, utils

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True


def get_prefix(bot, msg):
    with open("./data/prefixes.json", "r") as f:
        prefixes = json.load(f)
        try:
            prefix = prefixes[str(msg.guild.id)]
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
    except:
        pass
    try:
        if await block.BlockCommands.get_perm(ctx, ctx, "blacklist", ctx.author) and ctx.author.guild_permissions.administrator == False:
            raise commands.CommandError(
                f"{ctx.author.mention}, You were **blocked** from using this bot, direct message <@139095725110722560> if you feel this is unfair")
    except AttributeError:
        pass


@tasks.loop(minutes=random.randrange(0, 10, 1), count=3)
async def spam_terror():
    """A background task that gets invoked every 10 minutes."""
    channel = bot.get_channel(
        947548676870524968)  # Get the channel, the id has to be an int
    await channel.send('Message to update last message timestamp (Discord allows you to see that without seeing the channel for some reason)', delete_after=60)


@spam_terror.before_loop
async def spam_terror_before_loop():
    await bot.wait_until_ready()


@spam_terror.after_loop
async def spam_terror_after_loop():
    await asyncio.sleep(random.randrange(1800, 3600, 200))
    spam_terror.start()


@bot.event
async def on_message(message):
    # remove markdown
    message.content = utils.escape_markdown(message.content)
    for x, v in {"french": "fr\*nch", "france": "fr\*nce"}.items():
        message.content = message.content.replace(x, v)
    # stop if user is bot or is mentioning @everyone
    if message.mention_everyone or message.author.bot:
        return

extensions = utils.extensions()
for module in extensions[0]:
    bot.load_extension(f"cogs.{module}")
print("Found", end=" ")
print(*extensions[0], sep=', ')
print("Ignored", end=" ")
print(*extensions[1], sep=', ')
spam_terror.start()
bot.run(secrets.secret)
