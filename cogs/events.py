import main
import discord
from discord.ext import commands
# data
import json
import time
import random
# cogs
from cogs import utils, users, configs
# afk command data
import datetime
import humanize


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
    async def slash_command_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, commands.BotMissingPermissions):
            raise error
        elif isinstance(error, commands.CommandOnCooldown):
            e = discord.Embed(description=f"`❌` {error}", color=0xFF6969)
            await utils.sendembed(ctx, e, show_all=False)
        elif isinstance(error, discord.ApplicationCommandError):
            e = discord.Embed(description=f"`❌` {error}", color=0xFF6969)
            await utils.sendembed(ctx, e, show_all=False)
        raise error

    @commands.Cog.listener("on_command_error")
    async def command_error(self, ctx, error):
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
        with open('./data/afk.json', 'r') as f:
            afk = json.load(f)
        await users.UserUtils.update_data(afk, member)
        with open('./data/afk.json', 'w') as f:
            json.dump(afk, f, indent=4, sort_keys=True)

    @commands.Cog.listener("on_guild_join")
    async def guild_add_data(self, guild):
        with open('./data/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = '-'
        with open('./data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        """with open('./data/channels.json', 'r') as f:
            channels = json.load(f)
        channels[str(guild.id)] = {}
        with open('./data/channels.json', 'w') as f:
            json.dump(channels, f, indent=4)"""

    @commands.Cog.listener("on_guild_remove")
    async def guild_remove_data(self, guild):
        with open('./data/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open('./data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        """with open('./data/channels.json', 'r') as f:
            channels = json.load(f)
        channels.pop(str(guild.id))
        with open('./data/channels.json', 'w') as f:
            json.dump(channels, f, indent=4)"""

    @commands.Cog.listener("on_message")
    async def memes_channel(self, message):
        # delete messages in Northstar memes :dread:
        if message.channel.id == 973438217196040242:
            await message.delete(delay=random.randrange(100, 3600, 100))

    @commands.Cog.listener("on_message")
    async def afk_check(self, message):
        # check if user is afk or members in message
        prefix = main.get_prefix(self.bot, message)
        send = False
        afk_alert = discord.Embed(
            title=f"Members in your message are afk:")
        afk_alert.set_footer(
            text=f"Toggle: {prefix}alerts\nDMs Toggle: {prefix}dmalerts")
        if message.author.bot:
            return

        for member in message.mentions:
            if member.bot or member.id == message.author.id:
                return
            if self.bot.afk[f'{member.id}']['AFK']:
                send = True

                # gets afk message
                reason = self.bot.afk[f'{member.id}']['reason']

                # gets unix time
                unix_time = int(time.time()) - \
                    int(self.bot.afk[f'{member.id}']['time'])

                # user was afk for time.now() - time
                afktime = humanize.naturaltime(
                    datetime.datetime.now() - datetime.timedelta(seconds=unix_time))

                # add embed
                afk_alert.add_field(
                    name=f"{member.display_name.replace('[AFK]', '')} - {afktime}", value=f"\"{reason}\"", inline=True)

                # plus 1 time mentioned in afk.json
                self.bot.afk[f'{member.id}']['mentions'] = int(
                    self.bot.afk[f'{member.id}']['mentions']) + 1

                # save json
                configs.save(self.bot.afk_path, 'w', self.bot.afk)

        if send:
            await users.UserUtils.sendafk(self, message, ["afk_alert", "afk_alert_dm"], afk_alert)
        await users.UserUtils.update_data(self.bot.afk, message.author)
        # if message's author is afk continue
        if list(message.content.split())[0] != f'{prefix}afk' and self.bot.afk[f'{message.author.id}']['AFK']:
            # unix now - unix since afk
            timeafk = int(time.time()) - \
                int(self.bot.afk[f'{message.author.id}']['time'])

            # make time readable for user
            afktime = users.UserUtils.period(datetime.timedelta(
                seconds=round(timeafk)), "{d}d {h}h {m}m {s}s")

            # get mentions
            mentionz = self.bot.afk[f'{message.author.id}']['mentions']

            # make embed
            welcome_back = discord.Embed(
                description=f"**Welcome back {message.author.mention}!**")
            welcome_back.add_field(name="Afk for", value=afktime, inline=True)
            welcome_back.add_field(
                name="Mentioned", value=f"{mentionz} time(s)", inline=True)
            welcome_back.set_footer(
                text=f"Toggle: {prefix}wbalerts\nDMs Toggle: {prefix}wbdmalerts")

            # reset afk for user
            self.bot.afk[f'{message.author.id}']['AFK'] = False
            self.bot.afk[f'{message.author.id}']['reason'] = 'None'
            self.bot.afk[f'{message.author.id}']['time'] = '0'
            self.bot.afk[f'{message.author.id}']['mentions'] = 0
            configs.save(self.bot.afk_path, 'w', self.bot.afk)

            # try to reset nickname
            try:
                nick = message.author.display_name.replace('[AFK]', '')
                await message.author.edit(nick=nick)
            except:
                print(
                    f'I wasnt able to edit [{message.author} / {message.author.id}].')

            await users.UserUtils.sendafk(self, message, ["wb_alert", "wb_alert_dm"], welcome_back)
        configs.save(self.bot.afk_path, 'w', self.bot.afk)

    @commands.Cog.listener("on_message")
    async def help_check(self, message):
        # check if user's message is only bot ping and reply with help, if not process commands
        if message.author.bot == False and self.bot.user.mentioned_in(message) and len(message.content) == len(self.bot.user.mention):
            await message.reply(embed=discord.Embed(description=f'My prefix is `{self.bot.guild_prefixes[str(message.guild.id)]}` or {self.bot.user.mention}, you can also use slash commands\nFor more info use the /help command!'), delete_after=20, mention_author=False)
        else:
            await self.bot.process_commands(message)

    @commands.Cog.listener("on_message")
    async def word_trigger(self, message):
        for trigger, reply in self.bot.triggers.items():
            multi_trigger = list(trigger.split(' ⨉ '))
            for triggers in multi_trigger:
                if triggers in message.content.lower():
                    reply = random.choice(list(reply.split(' ⨉ ')))
                    await message.reply(reply)


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
