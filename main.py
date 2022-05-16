import json
import discord
import random
from discord.ext import commands, bridge, tasks
# cogs
import secrets
from cogs import block, utils, other

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True


def get_prefix(bot, msg):
    with open("./data/prefixes.json", "r") as f:
        prefixes = json.load(f)
        try:
            prefix = prefixes.get(str(msg.guild.id))
        except AttributeError:
            prefix = "-"
    return prefix


def when_mentioned_or_function(func):
    def inner(bot, msg):
        r = list(func(bot, msg))
        r = commands.when_mentioned(bot, msg) + r
        return r
    return inner


bot = bridge.Bot(
    command_prefix=when_mentioned_or_function(get_prefix), intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    # if isinstance(error, commands.CommandOnCooldown):
    # await ctx.respond(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s', ephemeral=True)
    # if isinstance(error, commands.MissingPermissions):
    # await ctx.respond(f'{ctx.author.mention} You\'re missing permissions for this command', ephemeral=True)
    if isinstance(error, commands.BotMissingPermissions):
        raise error
    elif isinstance(error, commands.CommandOnCooldown):
        e = discord.Embed(description=error, color=0xFF6969)
        await utils.sendembed(ctx, e, show_all=False)
    elif isinstance(error, discord.ApplicationCommandError):
        e = discord.Embed(description=error, color=0xFF6969)
        await utils.sendembed(ctx, e, show_all=False)
    raise error


@bot.event
async def on_command_error(ctx, error):
    # if isinstance(error, commands.CommandOnCooldown):
    # await ctx.reply(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s')
    # if isinstance(error, commands.MissingPermissions):
    # await ctx.reply(f'{ctx.author.mention} You\'re missing permissions for this command')
    if isinstance(error, commands.CommandNotFound):
        raise error
    elif isinstance(error, commands.BotMissingPermissions):
        raise error
    elif isinstance(error, commands.CommandError):
        e = discord.Embed(description=f"❌ {error}", color=0xFF6969)
        await utils.sendembed(ctx, e, delete=3)
    raise error


@bot.event
async def on_member_join(member):
    await other.OtherUtils.afkjoin(member)


@bot.event
async def on_guild_join(guild):
    with open('./data/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = '-'
    with open('./data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    with open('./data/perms.json', 'r') as f:
        perms = json.load(f)
    perms[str(guild.id)] = {}
    with open('./data/perms.json', 'w') as f:
        json.dump(perms, f, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open('./data/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes.pop(str(guild.id))
    with open('./data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    with open('./data/perms.json', 'r') as f:
        perms = json.load(f)
    perms.pop(str(guild.id))
    with open('./data/perms.json', 'w') as f:
        json.dump(perms, f, indent=4)


@bot.before_invoke
async def on_command(ctx):
    try:
        if await block.BlockUtils.get_perm("blacklist", ctx.author) and ctx.author.guild_permissions.administrator == False:
            raise commands.CommandError(
                f"{ctx.author.mention}, You were **blocked** from using this bot, direct message <@139095725110722560> if you feel this is unfair")
    except AttributeError:
        pass


@tasks.loop(minutes=random.randrange(0, 10, 1))
async def spam_terror():
    """A background task that gets invoked every 10 minutes."""
    channel = bot.get_channel(
        947548676870524968)  # Get the channel, the id has to be an int
    await channel.send('helou', delete_after=1)


@spam_terror.before_loop
async def spam_terror_before_loop():
    await bot.wait_until_ready()


@bot.event
async def on_message(message):
    # remove @everyone ` and \
    disable = ['`', '\\', '@everyone']
    for item in disable:
        message.content = message.content.replace(item, '')

    # delete messages in Northstar memes :dread:
    if message.channel.id == 973438217196040242:
        await message.delete(delay=random.randrange(100, 3600, 100))

    # check if user isnt bot and isnt mentioning @everyone
    if message.mention_everyone or message.author.bot:
        return

    # check if user is afk
    await other.OtherUtils.afkcheck(message)

    # check if user's message is only bot ping and reply with help, if not process commands
    if message.author.bot == False and bot.user.mentioned_in(message) and len(message.content) == len(bot.user.mention):
        await message.reply(embed=discord.Embed(description=f'My prefix is `{get_prefix(bot, message)}` or {bot.user.mention}, you can also use slash commands\nFor more info use the /help command!'), delete_after=20, mention_author=False)
    else:
        await bot.process_commands(message)

extensions = utils.extensions()
for module in extensions[0]:
    bot.load_extension(f"cogs.{module}")
print("Found", end=" ")
print(*extensions[0], sep=', ')
print("Ignored", end=" ")
print(*extensions[1], sep=', ')
spam_terror.start()
bot.run(secrets.secret)
