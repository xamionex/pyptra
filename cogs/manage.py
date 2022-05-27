import json
import discord
import os
import sys
import main
from discord.ext import commands
from cogs import utils

extensions = utils.extensions()


def setup(bot):
    bot.add_cog(ManageCommands(bot))


class ManageCommands(commands.Cog, name="Manage"):
    """Commands for managing the bot."""
    COG_EMOJI = "🛠️"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(hidden=True, name="log")
    @commands.is_owner()
    async def log(self, ctx):
        args = ctx.message.content.split(" ")
        if args[1] == "ctx":
            find = getattr(ctx, args[2])
        else:
            find = getattr(getattr(self, args[1]), args[2])
        print(find)
        await utils.sendembed(ctx, discord.Embed(description=find), show_all=False, delete=3, delete_speed=5)

    @commands.command(hidden=True, name="load")
    @commands.is_owner()
    async def load(self, ctx, *, module: str):
        """Loads a module"""
        e = discord.Embed(
            description=f"Trying to load modules \"{module}\"", color=0x69FF69)
        module = module.split(sep=" ")
        for cog in module:
            if cog in extensions[0]:
                self.ctx.load_extension(f"cogs.{cog}")
                e.add_field(name=f"{cog}", value="`✅` Success")
            else:
                e.add_field(name=f"{cog}", value="`❌` Not found")
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=5)

    @commands.command(hidden=True, name="unload")
    @commands.is_owner()
    async def unload(self, ctx, *, module: str):
        """Unloads a module"""
        e = discord.Embed(
            description=f"Trying to unload modules \"{module}\"", color=0x69FF69)
        module = module.split(sep=" ")
        for cog in module:
            if cog in extensions[0]:
                self.ctx.unload_extension(f"cogs.{cog}")
                e.add_field(name=f"{cog}", value="`✅` Success")
            else:
                e.add_field(name=f"{cog}", value="`❌` Not found")
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=5)

    @commands.command(hidden=True, name="reload")
    @commands.is_owner()
    async def reload(self, ctx, *, module: str):
        """Reloads a module"""
        e = discord.Embed(
            description=f"Trying to reload modules \"{module}\"", color=0x69FF69)
        module = module.split(sep=" ")
        for cog in module:
            if cog in extensions[0]:
                self.ctx.reload_extension(f"cogs.{cog}")
                e.add_field(name=f"{cog}", value="`✅` Success")
            elif cog == "all":
                for cog in extensions[0]:
                    self.ctx.reload_extension(f"cogs.{cog}")
                    e.add_field(name=f"{cog}", value="`✅` Success")
            else:
                e.add_field(name=f"{cog}", value="`❌` Not found")
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=5)

    @commands.command(hidden=True, name="restart")
    @commands.is_owner()
    async def restart(self, ctx):
        """Restarts the bot"""
        await utils.delete_message(ctx)
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(hidden=True, name="modules")
    @commands.is_owner()
    async def modules(self, ctx):
        """Lists modules"""
        modules = ", ".join(extensions[0])
        e = discord.Embed(title=f'Modules found:',
                          description=modules, color=0x69FF69)
        await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=5)

    @commands.command(hidden=True, name="prefix")
    @commands.is_owner()
    async def prefix(self, ctx, prefix=None):
        """Shows or changes prefix"""
        if prefix is not None:
            with open('./data/prefixes.json', 'r') as f:
                prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
            with open('./data/prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await utils.sendembed(ctx, discord.Embed(description=f'Prefix changed to: {prefix}'), False, 3, 5)
        else:
            await utils.sendembed(ctx, discord.Embed(description=f'My prefix is `{main.get_prefix(ctx, ctx.message)}` or {ctx.user.mention}, you can also use slash commands\nFor more info use the /help command!'), False, 3, 20)
