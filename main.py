import discord
from discord.ext import commands, bridge

import secrets
from cogs import utils, suggestions, other, block, info, fun

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = bridge.Bot(command_prefix=commands.when_mentioned_or(
    "-"), intents=intents, help_command=None)


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
        e = discord.Embed(description=error, color=0xFF6969)
        await utils.sendembed(ctx, e, delete=3)
    raise error


@bot.event
async def on_member_join(member):
    await other.OtherUtils.afkjoin(member)


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


@bot.before_invoke
async def on_command(ctx):
    if await block.BlockUtils.get_blacklist(ctx.author) and ctx.author.guild_permissions.administrator == False:
        raise commands.CommandError(
            f"{ctx.author.mention}, You were **blocked** from using this bot, direct message <@139095725110722560> if you feel this is unfair")


@bot.event
async def on_message(message):
    disable = {'`': '', '\\': '', '@everyone': ''}
    for key, value in disable.items():
        message.content = message.content.replace(key, value)
    # if message.author.bot:
        # return
    if message.mention_everyone:
        return
    for member in message.mentions:
        if member.bot:
            return
    await other.OtherUtils.afkcheck(message)
    if message.author.bot == False and bot.user.mentioned_in(message) and len(message.content) == len(bot.user.mention):
        await message.reply(f'My prefix is `-` or {bot.user.mention}, you can also use slash commands\nFor more info use the /help command!')
    else:
        await bot.process_commands(message)


bot.add_cog(suggestions.SuggestionCommands(bot))
bot.add_cog(other.OtherCommands(bot))
bot.add_cog(info.InfoCommands(bot))
bot.add_cog(block.BlockCommands(bot))
bot.add_cog(fun.FunCommands(bot))

bot.run(secrets.secret)
