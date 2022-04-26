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
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s')
    else:
        raise error
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention} You\'re missing permissions for this command')
    else:
        raise error

#@bot.event
#async def on_member_join(member):
#    await other.OtherUtils.afkjoin(member)

@bot.event
async def on_message(message):
    if (message.author.bot):
        return
    if message.mention_everyone or message.content == "@everyone":
        await message.channel.send("Please don't try this again.", reference=message, delete_after=10)
        return
    await other.OtherUtils.afkcheck(message)
    await bot.process_commands(message)

bot.add_cog(suggestions.SuggestionCommands(bot))
bot.add_cog(other.OtherCommands(bot))
bot.add_cog(info.InfoCommands(bot))
bot.add_cog(block.BlockCommands(bot))
bot.add_cog(fun.FunCommands(bot))

bot.run(secrets.secret)
