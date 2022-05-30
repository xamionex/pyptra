import discord
import os
import sys
from discord.ext import commands
from cogs import utils, configs

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
        elif args[1] == "self.ctx":
            find = getattr(self.ctx, args[2])
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
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix=None):
        """Shows or changes prefix"""
        if prefix is not None:
            prefixes = self.ctx.prefixes
            prefixes[str(ctx.guild.id)] = prefix
            configs.save(self.ctx.prefixes_path, "w", prefixes)
            await utils.sendembed(ctx, discord.Embed(description=f'Prefix changed to: {prefix}'), False, 3, 5)
        else:
            await utils.sendembed(ctx, discord.Embed(description=f'My prefix is `{self.ctx.guild_prefixes[str(ctx.guild.id)]}` or {self.ctx.user.mention}, you can also use slash commands\nFor more info use the /help command!'), False, 3, 20)

    @commands.group(hidden=True, name="triggers", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def triggers(self, ctx):
        """Triggers that reply whenever someone mentions a trigger"""
        await utils.senderror(ctx, f"No command specified, do {self.ctx.guild_prefixes[str(ctx.guild.id)]}help triggers for more info")

    @triggers.group(hidden=True, name="match", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def match(self, ctx):
        """Text triggers that have a match in one of the user's words"""
        await utils.senderror(ctx, f"No command specified, do {self.ctx.guild_prefixes[str(ctx.guild.id)]}help triggers match for more info")

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
        f"""Adds a match message trigger (ex. {self.ctx.guild_prefixes[str(ctx.guild.id)]}triggers match add trigger|anothertrigger this is the reply)"""
        await self.addtrigger(ctx, trigger, reply, "match")

    @match.command(hidden=True, name="rem")
    @commands.has_permissions(administrator=True)
    async def matchremovetrigger(self, ctx, *, trigger: str):
        f"""Removes a match message trigger (ex. {self.ctx.guild_prefixes[str(ctx.guild.id)]}triggers match del this|trigger other|trigger)"""
        await self.removetrigger(ctx, trigger, "match")

    @triggers.group(hidden=True, name="regex", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def regex(self, ctx):
        """Text triggers that have a regex match in one of the user's words"""
        await utils.senderror(ctx, f"No command specified, do {self.ctx.guild_prefixes[str(ctx.guild.id)]}help triggers regex for more info")

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
        f"""Adds a regex message trigger, underscores are replaced with a space (ex. {self.ctx.guild_prefixes[str(ctx.guild.id)]}triggers regex add this_trigger|another_trigger this is the reply)"""
        await self.addtrigger(ctx, trigger, reply, "regex")

    @regex.command(hidden=True, name="rem")
    @commands.has_permissions(administrator=True)
    async def regexremovetrigger(self, ctx, *, trigger: str):
        f"""Removes a regex message trigger, underscores are replaced with a space (ex. {self.ctx.guild_prefixes[str(ctx.guild.id)]}triggers regex del this|trigger another_trigger)"""
        await self.removetrigger(ctx, trigger, "regex")

    async def define_triggers(self, ctx):
        triggers = self.ctx.triggers
        if str(ctx.guild.id) not in triggers:
            triggers[str(ctx.guild.id)] = {}
            triggers[str(ctx.guild.id)]["regex"] = {}
            triggers[str(ctx.guild.id)]["regex"]["toggle"] = False
            triggers[str(ctx.guild.id)]["regex"]["triggers"] = {}
            triggers[str(ctx.guild.id)]["match"] = {}
            triggers[str(ctx.guild.id)]["match"]["toggle"] = False
            triggers[str(ctx.guild.id)]["match"]["triggers"] = {}
        return triggers

    async def toggletriggers(self, ctx, type: str):
        triggers = await self.define_triggers(ctx)
        if triggers[str(ctx.guild.id)][type]["toggle"]:
            triggers[str(ctx.guild.id)][type]["toggle"] = False
            await utils.sendembed(ctx, discord.Embed(description=f"❌ Disabled {type} triggers", color=0xFF6969), False)
        else:
            triggers[str(ctx.guild.id)][type]["toggle"] = True
            await utils.sendembed(ctx, discord.Embed(description=f"✅ Enabled {type} triggers", color=0x66FF99), False)
        configs.save(self.ctx.triggers_path, "w", triggers)

    async def listtriggers(self, ctx, type: str):
        triggers = await self.define_triggers(ctx)
        if triggers[str(ctx.guild.id)][type]["triggers"]:
            e = discord.Embed(description=f"Triggers found:")
            for trigger, reply in triggers[str(ctx.guild.id)][type]["triggers"].items():
                if type == "regex":
                    trigger = trigger.replace(" ", "_")
                e.add_field(name=trigger, value=reply)
            await utils.sendembed(ctx, e, show_all=False, delete=3, delete_speed=20)
        else:
            await utils.senderror(ctx, "No triggers found")

    async def addtrigger(self, ctx, trigger: str, reply: str, type: str):
        triggers = await self.define_triggers(ctx)
        triggers_list = triggers[str(ctx.guild.id)][type]["triggers"]
        if type == "regex":
            trigger = trigger.replace("_", " ")
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
        await utils.sendembed(ctx, e, False)
        configs.save(self.ctx.triggers_path, "w", triggers)

    async def removetrigger(self, ctx, trigger: str, type: str):
        triggers = await self.define_triggers(ctx)
        triggers_list = triggers[str(ctx.guild.id)][type]["triggers"]
        trigger = trigger.split(" ")
        e = discord.Embed(
            title=f"🛠️ Trying to remove triggers:", color=0x66FF99)
        for item in trigger:
            try:
                if type == "regex":
                    item = item.replace("_", " ")
                reply = triggers_list[str(item)]
                triggers_list.pop(str(item))
                e.add_field(
                    name=f"✅ Removed {item.replace(' ', '_')}", value=f"`{reply}`")
            except:
                e.add_field(name="❌ Couldn't find", value=f"`{item}`")
        await utils.sendembed(ctx, e, False)
        configs.save(self.ctx.triggers_path, "w", triggers)
