import discord
import os
import sys
from discord.ext import commands
from cogs.configs import Configs
from cogs.utils import Utils


def setup(bot):
    bot.add_cog(ManageCommands(bot))


class ManageCommands(commands.Cog, name="Manage"):
    """Commands for managing the bot."""
    COG_EMOJI = "🛠️"

    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(hidden=True, name="load")
    @commands.is_owner()
    async def load(self, ctx, *, module: str):
        """Loads a module"""
        e = discord.Embed(
            description=f"Trying to load modules \"{module}\"", color=0x69FF69)
        module = module.split(sep=" ")
        for cog in module:
            if cog in self.ctx.extensions_list:
                self.ctx.load_extension(f"cogs.{cog}")
                e.add_field(name=f"{cog}", value="`✅` Success")
            else:
                e.add_field(name=f"{cog}", value="`❌` Not found")
        await Utils.delete_command_message(ctx, 5)
        await ctx.respond(embed=e, delete_after=5)

    @commands.command(hidden=True, name="unload")
    @commands.is_owner()
    async def unload(self, ctx, *, module: str):
        """Unloads a module"""
        e = discord.Embed(
            description=f"Trying to unload modules \"{module}\"", color=0x69FF69)
        module = module.split(sep=" ")
        for cog in module:
            if cog in self.ctx.extensions_list:
                self.ctx.unload_extension(f"cogs.{cog}")
                e.add_field(name=f"{cog}", value="`✅` Success")
            else:
                e.add_field(name=f"{cog}", value="`❌` Not found")
        await Utils.delete_command_message(ctx, 5)
        await ctx.respond(embed=e, delete_after=5)

    @commands.command(hidden=True, name="reload")
    @commands.is_owner()
    async def reload(self, ctx, *, module: str):
        """Reloads a module"""
        e = discord.Embed(
            description=f"Trying to reload modules \"{module}\"", color=0x69FF69)
        module = module.split(sep=" ")
        for cog in module:
            if cog in self.ctx.extensions_list:
                self.ctx.reload_extension(f"cogs.{cog}")
                e.add_field(name=f"{cog}", value="`✅` Success")
            elif cog == "all":
                for cog in self.ctx.extensions_list:
                    self.ctx.reload_extension(f"cogs.{cog}")
                    e.add_field(name=f"{cog}", value="`✅` Success")
            else:
                e.add_field(name=f"{cog}", value="`❌` Not found")
        await Utils.delete_command_message(ctx, 5)
        await ctx.respond(embed=e, delete_after=5)

    @commands.command(hidden=True, name="restart")
    @commands.is_owner()
    async def restart(self, ctx):
        """Restarts the bot"""
        await Utils.delete_command_message(ctx)
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(hidden=True, name="modules")
    @commands.is_owner()
    async def modules(self, ctx):
        """Lists modules"""
        modules = ", ".join(self.ctx.extensions_list)
        e = discord.Embed(title=f'Modules found:', description=modules, color=0x69FF69)
        await ctx.respond(embed=e)

    @commands.command(hidden=True, name="prefix")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix=None):
        """Shows or changes prefix"""
        if prefix is not None:
            self.ctx.settings[str(ctx.guild.id)]["prefix"] = prefix
            Configs.save(self.ctx.settings_path, "w", self.ctx.settings)
            await ctx.respond(embed=discord.Embed(description=f"Prefix changed to: {prefix}"))
        else:
            await ctx.respond(embed=discord.Embed(description=f"My prefix is `{self.ctx.settings[str(ctx.guild.id)]['prefix']}` or {self.ctx.user.mention}, you can also use slash commands\nFor more info use the /help command!"))

    @commands.group(hidden=True, name="triggers", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def triggers(self, ctx):
        """Triggers that reply whenever someone mentions a trigger"""
        await Utils.send_error(ctx, f"No command specified, do {self.ctx.settings[str(ctx.guild.id)]['prefix']}help triggers for more info")

    @triggers.group(hidden=True, name="match", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def match(self, ctx):
        """Text triggers that have a match in one of the user's words"""
        await Utils.send_error(ctx, f"No command specified, do {self.ctx.settings[str(ctx.guild.id)]['prefix']}help triggers match for more info")

    @match.command(hidden=True, name="toggle")
    @commands.has_permissions(administrator=True)
    async def matchtoggletriggers(self, ctx):
        """Toggles match message triggers"""
        await self.toggletriggers(ctx, "match")

    @match.command(hidden=True, name="list")
    @commands.has_permissions(administrator=True)
    async def matchlisttriggers(self, ctx):
        """Lists match message triggers"""
        await self.listtriggers(ctx, "match")

    @match.command(hidden=True, name="add")
    @commands.has_permissions(administrator=True)
    async def matchaddtrigger(self, ctx, trigger: str, *, reply: str):
        f"""Adds a match message trigger (ex. {self.ctx.settings[str(ctx.guild.id)]['prefix']}triggers match add trigger|anothertrigger this is the reply)"""
        await self.addtrigger(ctx, trigger, reply, "match")

    @match.command(hidden=True, name="rem")
    @commands.has_permissions(administrator=True)
    async def matchremovetrigger(self, ctx, *, trigger: str):
        f"""Removes a match message trigger (ex. {self.ctx.settings[str(ctx.guild.id)]['prefix']}triggers match del this|trigger other|trigger)"""
        await self.removetrigger(ctx, trigger, "match")

    @triggers.group(hidden=True, name="regex", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def regex(self, ctx):
        """Text triggers that have a regex match in one of the user's words"""
        await Utils.send_error(ctx, f"No command specified, do {self.ctx.settings[str(ctx.guild.id)]['prefix']}help triggers regex for more info")

    @regex.command(hidden=True, name="toggle")
    @commands.has_permissions(administrator=True)
    async def regextoggletriggers(self, ctx):
        """Toggles regex message triggers"""
        await self.toggletriggers(ctx, "regex")

    @regex.command(hidden=True, name="list")
    @commands.has_permissions(administrator=True)
    async def regexlisttriggers(self, ctx):
        """Lists regex message triggers"""
        await self.listtriggers(ctx, "regex")

    @regex.command(hidden=True, name="add")
    @commands.has_permissions(administrator=True)
    async def regexaddtrigger(self, ctx, trigger: str, *, reply: str):
        f"""Adds a regex message trigger, underscores are replaced with a space (ex. {self.ctx.settings[str(ctx.guild.id)]['prefix']}triggers regex add this_trigger|another_trigger this is the reply)"""
        await self.addtrigger(ctx, trigger, reply, "regex")

    @regex.command(hidden=True, name="rem")
    @commands.has_permissions(administrator=True)
    async def regexremovetrigger(self, ctx, *, trigger: str):
        f"""Removes a regex message trigger, underscores are replaced with a space (ex. {self.ctx.settings[str(ctx.guild.id)]['prefix']}triggers regex del this|trigger another_trigger)"""
        await self.removetrigger(ctx, trigger, "regex")

    async def define_triggers(self, ctx):
        settings = self.ctx.settings[str(ctx.guild.id)]
        if len(settings["triggers"]) <= 0:
            settings["triggers"] = {
                "match": {
                    "toggle": False,
                    "triggers": {}
                },
                "regex": {
                    "toggle": False,
                    "triggers": {}
                }
            }
        Configs.save(self.ctx.settings_path, "w", self.ctx.settings)
        return settings["triggers"]

    async def toggletriggers(self, ctx, type: str):
        settings = await ManageCommands.define_triggers(self, ctx)
        if settings[str(type)]["toggle"]:
            settings[str(type)]["toggle"] = False
            await ctx.respond(embed=discord.Embed(description=f"❌ Disabled {type} triggers", color=0xFF6969))
        else:
            settings[str(type)]["toggle"] = True
            await ctx.respond(embed=discord.Embed(description=f"✅ Enabled {type} triggers", color=0x66FF99))
        Configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    async def listtriggers(self, ctx, type: str):
        settings = await ManageCommands.define_triggers(self, ctx)
        if settings[str(type)]["triggers"]:
            e = discord.Embed(description=f"Triggers found:")
            for trigger, reply in settings[str(type)]["triggers"].items():
                if type == "regex":
                    trigger = trigger.replace(" ", "_")
                e.add_field(name=trigger, value=reply)
            await ctx.respond(embed=e)
        else:
            await Utils.send_error(ctx, "No triggers found")

    async def addtrigger(self, ctx, trigger: str, reply: str, type: str):
        settings = await ManageCommands.define_triggers(self, ctx)
        triggers_list = settings[str(type)]["triggers"]
        e = discord.Embed(title=f"🛠️ Trying to add trigger:", color=0x66FF99)
        old_reply = None
        try:
            old_reply = triggers_list[trigger]
        except:
            pass
        triggers_list[trigger] = reply
        if old_reply is not None:
            e.add_field(
                name=f"Overwrote: {', '.join(trigger.split('|'))}", value=f"**Old reply:** `{old_reply}`\n**New reply:** `{triggers_list[trigger]}`")
        else:
            e.add_field(
                name=f"Trigger: {', '.join(trigger.split('|'))}", value=f"**Reply:** `{reply}`")
        await ctx.respond(embed=e)
        Configs.save(self.ctx.settings_path, "w", self.ctx.settings)

    async def removetrigger(self, ctx, trigger: str, type: str):
        settings = await ManageCommands.define_triggers(self, ctx)
        triggers_list = settings[str(type)]["triggers"]
        try:
            reply = triggers_list[str(trigger)]
            triggers_list.pop(str(trigger))
            e = discord.Embed(title=f"✅ Removed {trigger}", description=f"`{reply}`", color=0x66FF99)
        except:
            e = discord.Embed(title=f"❌ Couldn't find", description=f"`{trigger}`", color=0xFF6969)
        await ctx.respond(embed=e)
        Configs.save(self.ctx.settings_path, "w", self.ctx.settings)
