import discord
from discord.ext import commands

import secrets
import cogs.suggestions as suggestions
import cogs.other as other
import cogs.block as block
import cogs.info as info
import cogs.fun as fun

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("-"), intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    #if isinstance(error, commands.CommandOnCooldown):
        #await ctx.respond(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s', ephemeral=True)
    #if isinstance(error, commands.MissingPermissions):
        #await ctx.respond(f'{ctx.author.mention} You\'re missing permissions for this command', ephemeral=True)
    #if isinstance(error, commands.CommandNotFound):
        #await ctx.respond(f'{ctx.author.mention} This command doesn\'t exist', ephemeral=True)
    if isinstance(error, commands.CommandError):
        await ctx.respond(embed=discord.Embed(description=error), ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    #if isinstance(error, commands.CommandOnCooldown):
        #await ctx.reply(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s')
    #if isinstance(error, commands.MissingPermissions):
        #await ctx.reply(f'{ctx.author.mention} You\'re missing permissions for this command')
    #if isinstance(error, commands.CommandNotFound):
        #await ctx.reply(f'{ctx.author.mention} This command doesn\'t exist')
    if isinstance(error, commands.CommandError):
        await ctx.reply(embed=discord.Embed(description=error), delete_after=20, mention_author=False)

@bot.event
async def on_member_join(member):
    await other.OtherUtils.afkjoin(member)

@bot.before_invoke
async def on_command(ctx):
    if await block.BlockUtils.get_blacklist(ctx.author) != 0:
        raise discord.ext.commands.CommandError(f"{ctx.author.mention}, You were **blocked** from using this bot, direct message <@139095725110722560> if you feel this is unfair")

@bot.event
async def on_message(message):
    disable = {'`': '', '\\': '', '@everyone': ''}
    for key, value in disable.items():
        message.content = message.content.replace(key, value)
    #if message.author.bot:
        #return
    if message.mention_everyone:
        return
    await other.OtherUtils.afkcheck(message)
    await bot.process_commands(message)

bot.add_cog(suggestions.SuggestionCommands(bot))
bot.add_cog(other.OtherCommands(bot))
bot.add_cog(info.InfoCommands(bot))
bot.add_cog(block.BlockCommands(bot))
bot.add_cog(fun.FunCommands(bot))

bot.run(secrets.secret)
