import discord
from discord.ext import commands

import suggestions
import other
import secrets
import block
import info

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
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s')
    else:
        raise error
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention} You\'re missing permissions for this command')
    else:
        raise error

bot.add_cog(suggestions.SuggestionCommands(bot))
bot.add_cog(other.OtherCommands(bot))
bot.add_cog(info.InfoCommands(bot))
bot.add_cog(block.BlockCommands(bot))

bot.run(secrets.secret)
