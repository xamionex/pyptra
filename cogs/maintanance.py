import discord
import os
import sys
from discord.ext import commands
from cogs import utils

extensions = utils.extensions()


def setup(bot):
    bot.add_cog(MaintananceCommands(bot))


class MaintananceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, name="load", description="Loads a module")
    @commands.has_permissions(administrator=True)
    async def load(self, bot, module: str):
        if module in extensions[0]:
            self.bot.load_extension(module)
            await utils.sendembed(bot, discord.Embed(description=f'✅ {module} successfully loaded', color=0x69FF69), show_all=False, delete=3, delete_speed=20)
        else:
            await utils.senderror(bot, "Couldn't find module")

    @commands.command(hidden=True, name="unload", description="Unloads a module")
    @commands.has_permissions(administrator=True)
    async def unload(self, bot, module: str):
        if module in extensions[0]:
            self.bot.unload_extension(module)
            await utils.sendembed(bot, discord.Embed(description=f'✅ {module} successfully unloaded', color=0x69FF69), show_all=False, delete=3, delete_speed=20)
        else:
            await utils.senderror(bot, "Couldn't find module")

    @commands.command(hidden=True, name="reload", description="Reloads a module")
    @commands.has_permissions(administrator=True)
    async def reload(self, bot, module: str):
        if module in extensions[0]:
            self.bot.reload_extension(f"cogs.{module}")
            await utils.sendembed(bot, discord.Embed(description=f'✅ {module} successfully reloaded', color=0x69FF69), show_all=False, delete=3, delete_speed=20)
        elif module == "all":
            for module in extensions[0]:
                self.bot.reload_extension(f"cogs.{module}")
                await utils.sendembed(bot, discord.Embed(description=f'✅ {module} successfully reloaded', color=0x69FF69), show_all=False, delete=3, delete_speed=20)
        else:
            await utils.senderror(bot, "Couldn't find module")

    @commands.command(hidden=True, name="restart", description="Restarts the bot")
    @commands.has_permissions(administrator=True)
    async def restart(self, bot):
        await bot.message.delete()
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(hidden=True, name="modules", description="Lists modules")
    @commands.has_permissions(administrator=True)
    async def modules(self, bot):
        modules = ", ".join(extensions[0])
        e = discord.Embed(title=f'Modules found:',
                          description=modules, color=0x69FF69)
        await utils.sendembed(bot, e, show_all=False, delete=3, delete_speed=20)
