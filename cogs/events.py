import asyncio
import re
import json
import discord
import random
import main
from discord.ext import commands, tasks
# cogs
from cogs import block, utils, other


def setup(bot):
    bot.add_cog(Events(bot))
    # bot.add_cog(Loops(bot))


class Events(commands.Cog, name="Events"):
    """Event listeners (no commands)."""
    COG_EMOJI = "🛠️"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def logged_in(self):
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
        print("------")

    @commands.Cog.listener("on_application_command_error")
    async def slash_command_error(ctx: discord.ApplicationContext, error):
        # if isinstance(error, commands.CommandOnCooldown):
        # await ctx.respond(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s', ephemeral=True)
        # if isinstance(error, commands.MissingPermissions):
        # await ctx.respond(f'{ctx.author.mention} You\'re missing Permissions for this command', ephemeral=True)
        if isinstance(error, commands.BotMissingPermissions):
            raise error
        elif isinstance(error, commands.CommandOnCooldown):
            e = discord.Embed(description=error, color=0xFF6969)
            await utils.sendembed(ctx, e, show_all=False)
        elif isinstance(error, discord.ApplicationCommandError):
            e = discord.Embed(description=error, color=0xFF6969)
            await utils.sendembed(ctx, e, show_all=False)
        raise error

    @commands.Cog.listener("on_command_error")
    async def command_error(self, ctx, error):
        # if isinstance(error, commands.CommandOnCooldown):
        # await ctx.reply(f'{ctx.author.mention} You\'re on cooldown for {round(error.retry_after, 2)}s')
        # if isinstance(error, commands.MissingPermissions):
        # await ctx.reply(f'{ctx.author.mention} You\'re missing Permissions for this command')
        if isinstance(error, commands.CommandNotFound):
            raise error
        elif isinstance(error, commands.BotMissingPermissions):
            raise error
        elif isinstance(error, commands.CommandError):
            e = discord.Embed(description=f"`❌` {error}", color=0xFF6969)
            await utils.sendembed(ctx, e, delete=3)
        raise error

    @commands.Cog.listener("on_member_join")
    async def member_data(self, member):
        await other.OtherUtils.afkjoin(member)

    @commands.Cog.listener("on_guild_join")
    async def guild_add_data(self, guild):
        with open('./data/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = '-'
        with open('./data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        with open('./data/channels.json', 'r') as f:
            channels = json.load(f)
        channels[str(guild.id)] = {}
        with open('./data/channels.json', 'w') as f:
            json.dump(channels, f, indent=4)

    @commands.Cog.listener("on_guild_remove")
    async def guild_remove_data(self, guild):
        with open('./data/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open('./data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        with open('./data/channels.json', 'r') as f:
            channels = json.load(f)
        channels.pop(str(guild.id))
        with open('./data/channels.json', 'w') as f:
            json.dump(channels, f, indent=4)

    @commands.Cog.listener("on_message")
    async def memes_channel(self, message):
        # delete messages in Northstar memes :dread:
        if message.channel.id == 973438217196040242:
            await message.delete(delay=random.randrange(100, 3600, 100))

    @commands.Cog.listener("on_message")
    async def afk_check(self, message):
        # check if user is afk
        await other.OtherUtils.afkcheck(message)

    @commands.Cog.listener("on_message")
    async def help_check(self, message):
        # check if user's message is only bot ping and reply with help, if not process commands
        if message.author.bot == False and self.bot.user.mentioned_in(message) and len(message.content) == len(self.bot.user.mention):
            await message.reply(embed=discord.Embed(description=f'My prefix is `{main.get_prefix(self.bot, message)}` or {self.bot.user.mention}, you can also use slash commands\nFor more info use the /help command!'), delete_after=20, mention_author=False)
        else:
            await self.bot.process_commands(message)


"""
class Loops(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    async def spam_start(self, ctx, id, time, text):
        await self.define_seconds(time)
        await self.spam.start(self, ctx, {time: text})

    def define_seconds(time=1):
        return time

    @commands.command(name="spam")
    async def start_spam_now(self, ctx):
        self.spam.start()



    @commands.group()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def channels(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.CommandNotFound

    @channels.command()
    async def add(self, ctx, channel: discord.TextChannel, time, *, message):
        time_regex = re.compile("([0-9]+)(d|h|m|s)?")
        multiplier = {
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1,
            "None": 1  # if they type "30", this will be 30 seconds"
        }
        match = time_regex.match(time)

        if not match:
            raise commands.CommandError(
                "time is a required argument that is missing")

        seconds = int(match.groups()[0]) * \
            multiplier.get(str(match.groups()[1]))

        input_data = [channel, seconds, message]

        if await EventUtils.get_channel_bool(self, ctx, input_data):
            await utils.senderror(ctx, f"Channel already has repeating message.")
        else:
            await EventUtils.add_channel(self, ctx, input_data)
            e = discord.Embed(title="Repeating message made:")
            e.add_field(name="Message", value=message)
            e.add_field(name="Repeats each", value=f"{seconds}s")
            e.add_field(name="In channel", value=channel.mention)
            await utils.sendembed(ctx, e)
            await EventUtils.add_channel(self, ctx, input_data)

    @channels.command()
    async def remove(self, ctx, channel: discord.TextChannel):
        data = await EventUtils.get_data()
        if str(channel.id) in data[str(channel.guild.id)]:
            data[str(channel.guild.id)].pop(str(channel.id))
            await utils.sendembed(ctx, e=discord.Embed(description=f"Removed {channel.mention}", color=0x66FF99))
        else:
            await utils.senderror(ctx, f"{channel.mention} isn't in data")

    @channels.command()
    async def list(self, ctx):
        channel_data = await EventUtils.get_channels_active(self, ctx)
        e = discord.Embed(description="Active repeating messages:")
        for data in channel_data:
            for id, value in data.items():
                e.add_field(
                    name=f"{id} - every {value[1]}s", value=f"{value[0]}")
        await utils.sendembed(ctx, e)


class EventUtils():
    async def get_data():
        with open("./data/channels.json") as f:
            data = json.load(f)
            return data

    async def get_channels(guild):
        channels = []
        for channel in guild.text_channels:
            channels.append(channel)
        return channels

    async def get_channels_active(self, ctx):
        channel_list = []
        for guild in self.ctx.guilds:
            for channel in guild.text_channels:
                if await EventUtils.get_channel_bool(self, ctx, [channel]):
                    channel_data = await EventUtils.get_channel_data(self, ctx, channel)
                    channel_list.append(channel_data)
        return channel_list

    async def check_channel(self, ctx, input_data):
        data = await EventUtils.get_data()
        # if channel id isnt in guild
        if str(input_data[0].id) in data[str(input_data[0].guild.id)]:
            return False
        else:
            await EventUtils.set_channel(self, ctx, input_data, data)

    async def set_channel(self, ctx, input_data, data):
        data[str(input_data[0].guild.id)][str(input_data[0].id)] = {}
        data[str(input_data[0].guild.id)][str(input_data[0].id)]["on"] = False
        data[str(input_data[0].guild.id)][str(input_data[0].id)]["time"] = None
        data[str(input_data[0].guild.id)][str(input_data[0].id)]["text"] = None
        with open("./data/channels.json", "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
            return True

    async def get_channel_bool(self, ctx, input_data):
        await EventUtils.check_channel(self, ctx, input_data)
        data = await EventUtils.get_data()
        yn = data[str(input_data[0].guild.id)][str(input_data[0].id)]["on"]
        return yn

    async def get_channel_data(self, ctx, channel):
        await EventUtils.check_channel(self, ctx, [channel])
        data = await EventUtils.get_data()
        channel_id = data[str(channel.guild.id)][str(channel.id)]
        channel_data = {channel.id: [channel_id['text'], channel_id["time"]]}
        return channel_data

    async def add_channel(self, ctx, input_data):
        await EventUtils.check_channel(self, ctx, input_data)
        data = await EventUtils.get_data()
        data[str(input_data[0].guild.id)][str(input_data[0].id)]["on"] = True
        data[str(input_data[0].guild.id)][str(
            input_data[0].id)]["time"] = input_data[1]
        data[str(input_data[0].guild.id)][str(
            input_data[0].id)]["text"] = input_data[2]
        await EventUtils.dump(data)

    async def remove_channel(self, ctx, input_data):
        await EventUtils.check_channel(self, ctx, input_data)
        data = await EventUtils.get_data()
        data[str(input_data[0].guild.id)].pop(str(input_data[0].id))
        await EventUtils.check_channel(self, ctx, input_data)
        await EventUtils.dump(data)

    async def dump(data):
        with open("./data/channels.json", "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
"""
