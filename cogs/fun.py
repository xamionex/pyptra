import random
from petpetgif import petpet
import discord
from discord.ext import commands
from io import BytesIO
from typing import Union, Optional
from cogs.block import BlockUtils

hug_gifs = ["https://media1.tenor.com/images/7e30687977c5db417e8424979c0dfa99/tenor.gif",
            "https://media1.tenor.com/images/4d89d7f963b41a416ec8a55230dab31b/tenor.gif",
            "https://media1.tenor.com/images/45b1dd9eaace572a65a305807cfaec9f/tenor.gif",
            "https://media1.tenor.com/images/b4ba20e6cb49d8f8bae81d86e45e4dcc/tenor.gif",
            "https://media1.tenor.com/images/949d3eb3f689fea42258a88fa171d4fc/tenor.gif",
            "https://media1.tenor.com/images/72627a21fc298313f647306e6594553f/tenor.gif",
            "https://media1.tenor.com/images/d3dca2dec335e5707e668b2f9813fde5/tenor.gif",
            "https://media1.tenor.com/images/eee4e709aa896f71d36d24836038ed8a/tenor.gif",
            "https://media1.tenor.com/images/b214bd5730fd2fdfaae989b0e2b5abb8/tenor.gif",
            "https://media1.tenor.com/images/edea458dd2cbc76b17b7973a0c23685c/tenor.gif",
            "https://media1.tenor.com/images/506aa95bbb0a71351bcaa753eaa2a45c/tenor.gif",
            "https://media1.tenor.com/images/42922e87b3ec288b11f59ba7f3cc6393/tenor.gif",
            "https://media1.tenor.com/images/bb841fad2c0e549c38d8ae15f4ef1209/tenor.gif",
            "https://media1.tenor.com/images/234d471b1068bc25d435c607224454c9/tenor.gif",
            "https://media1.tenor.com/images/de06f8f71eb9f7ac2aa363277bb15fee/tenor.gif"]
hug_words = ['hugged', 'cuddled', 'embraced',
             'squeezed', 'is holding onto', 'is caressing']
hug_words_bot = ['hug', 'cuddle', 'embrace', 'squeeze', 'hold onto', 'caress']
kiss_gifs = ["https://c.tenor.com/YTsHLAJdOT4AAAAC/anime-kiss.gif",
             "https://c.tenor.com/wDYWzpOTKgQAAAAC/anime-kiss.gif",
             "https://c.tenor.com/F02Ep3b2jJgAAAAC/cute-kawai.gif",
             "https://c.tenor.com/Xc6y_eh0IcYAAAAd/anime-kiss.gif",
             "https://c.tenor.com/sDOs4aMXC6gAAAAd/anime-sexy-kiss-anime-girl.gif",
             "https://c.tenor.com/dp6A2wF5EKYAAAAC/anime-love.gif",
             "https://c.tenor.com/OOwVQiBrXiMAAAAC/good-morning.gif",
             "https://c.tenor.com/I8kWjuAtX-QAAAAC/anime-ano.gif",
             "https://c.tenor.com/TWbZjCy8iN4AAAAC/girl-anime.gif"]
kiss_words = ['kissed', 'smooched', 'embraced']
kiss_words_bot = ['kiss', 'smooch', 'embrace']


class FunCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    async def checkweird(self, ctx):
        if await BlockUtils.get_weird(ctx.author):
            raise commands.CommandError(
                f"{ctx.author.mention}, You aren\'t weird enough to use this.. (dm <@139095725110722560>)")
        else:
            return

    @commands.before_invoke(checkweird)
    @commands.command(name="pet", description="Pet someone :D")
    async def pet1(self, ctx, image: Optional[Union[discord.PartialEmoji, discord.member.Member]]):
        image = image or ctx.author
        e = await FunUtils.pet(ctx, image)
        await ctx.reply(embed=e[0], file=e[1], mention_author=False)

    @commands.before_invoke(checkweird)
    @commands.command(name="hug", description="Hug someone :O")
    async def hug(self, ctx, *, member: Optional[discord.Member]):
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(hug_words_bot))} me!", color=0x0690FF)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} {(random.choice(hug_words))} {member.mention}", color=0x0690FF)
        e.set_thumbnail(url=(random.choice(hug_gifs)))
        await ctx.reply(embed=e)

    @commands.before_invoke(checkweird)
    @commands.command(name="kiss", description="Kiss someone :O")
    async def kiss(self, ctx, *, member: Optional[discord.Member]):
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(kiss_words_bot))} me!", color=0x0690FF)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} {(random.choice(kiss_words))} {member.mention}", color=0x0690FF)
        e.set_thumbnail(url=(random.choice(kiss_gifs)))
        await ctx.reply(embed=e)


class FunUtils():
    async def pet(ctx, image):
        if type(image) == discord.PartialEmoji:
            image = await image.read()  # retrieve the image bytes
            what = "an emoji"
        elif type(image) == discord.member.Member:
            what = image.mention
            # retrieve the image bytes
            image = await image.avatar.with_format('png').read()
        else:
            await ctx.reply('Please use a custom emoji or tag a member to petpet their avatar.')
            return
        # file-like container to hold the emoji in memory
        source = BytesIO(image)
        dest = BytesIO()  # container to store the petpet gif in memory
        petpet.make(source, dest)
        # set the file pointer back to the beginning so it doesn't upload a blank file.
        dest.seek(0)
        filename = f"{image[0]}-petpet.gif"
        file = discord.File(dest, filename=filename)
        e = discord.Embed(description=f"{ctx.author.mention} has pet {what}")
        e.set_image(url=f"attachment://{filename}")
        return e, file
