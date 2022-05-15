from typing import Optional
import discord
from discord.ext import commands, bridge
from cogs import block, utils
import random
# get image from url
import io
import aiohttp
# image
from io import BytesIO
from petpetgif import petpet

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


def setup(bot):
    bot.add_cog(FunCommands(bot))


class FunCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx

    async def checkperm(self, ctx, perm):
        if await block.BlockUtils.get_perm(perm, ctx.author) or ctx.author.guild_permissions.administrator:
            return
        else:
            await utils.senderror(ctx, f"{ctx.author.mention}, You aren\'t allowed to use this")

    async def checkping(self, ctx, member):
        if await block.BlockUtils.get_perm("ping", member):
            await utils.senderror(ctx, f"This person has disallowed me from using them in commands.")

    @bridge.bridge_command(name="pet", description="Pet someone :D")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pet(self, ctx, member: Optional[discord.member.Member], emoji: Optional[discord.PartialEmoji], url=None):
        await self.checkperm(ctx, "pet")
        attachment = None
        try:
            attachment = ctx.message.attachments[0]
        except:
            pass
        image = member or emoji or attachment or url
        if type(image) == discord.PartialEmoji:
            what = "an emoji"
            image = await image.read()
        elif type(image) == discord.Attachment:
            what = "an image"
            image = await image.read()
        elif url is not None:
            url = ctx.message.content.split(" ")[1]
            disable = {'<': '', '>': ''}
            for key, value in disable.items():
                url = url.replace(key, value)
            what = "an image"
            async with aiohttp.ClientSession().get(url) as url:
                if url.status != 200:
                    await utils.senderror(ctx, "Could not download file")
                image = await url.read()
        elif type(image) == discord.member.Member:
            await self.checkping(ctx, image)
            what = image.mention
            image = await image.avatar.with_format('png').read()
        else:
            await utils.senderror(ctx, "Please use a custom emoji or tag a member to petpet their avatar.")
        # retrieve the image bytes above
        # file-like container to hold the emoji in memory
        source = BytesIO(image)  # sets image as "source"
        dest = BytesIO()  # container to store the petpet gif in memory
        # takes source (image) and makes pet-pet and puts into memory
        petpet.make(source, dest)
        # set the file pointer back to the beginning so it doesn't upload a blank file.
        dest.seek(0)
        filename = f"{image[0]}-petpet.gif"
        file = discord.File(dest, filename=filename)
        e = discord.Embed(description=f"{ctx.author.mention} has pet {what}")
        e.set_image(url=f"attachment://{filename}")
        if await utils.CheckInstance(ctx):
            await ctx.respond(embed=e, file=file, mention_author=False)
        else:
            await ctx.respond(embed=e, file=file)

    @commands.command(name="hug", description="Hug someone :O")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hug(self, ctx, *, member: Optional[discord.Member]):
        await self.checkperm(ctx, "weird")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(hug_words_bot))} me!", color=0x0690FF)
        else:
            await self.checkping(ctx, member)
            e = discord.Embed(
                description=f"{ctx.author.mention} {(random.choice(hug_words))} {member.mention}", color=0x0690FF)
        e.set_image(url=(random.choice(hug_gifs)))
        await utils.sendembed(ctx, e)

    @commands.command(name="kiss", description="Kiss someone :O")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def kiss(self, ctx, *, member: Optional[discord.Member]):
        await self.checkperm(ctx, "weird")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(kiss_words_bot))} me!", color=0x0690FF)
        else:
            await self.checkping(ctx, member)
            e = discord.Embed(
                description=f"{ctx.author.mention} {(random.choice(kiss_words))} {member.mention}", color=0x0690FF)
        e.set_image(url=(random.choice(kiss_gifs)))
        await utils.sendembed(ctx, e)

    @commands.command(name="fall", description="Make someone fall >:)")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def fall(self, ctx, *, member: Optional[discord.Member]):
        await self.checkperm(ctx, "joke")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you fell", color=0xFF6969)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} made {member.mention} fall!", color=0xFF6969)
        e.set_thumbnail(url=(
            "https://media.discordapp.net/attachments/854984817862508565/883437876493307924/image0-2.gif"))
        await utils.sendembed(ctx, e)

    @commands.command(name="promote", description="Promote someone :D")
    @commands.has_permissions(administrator=True)
    async def promote(self, ctx, member: discord.Member, *, message=None):
        await self.checkperm(ctx, "joke")
        if member == ctx.author:
            e = discord.Embed(
                description=f"{ctx.author.mention} promoted themselves to {message}", color=0xFF6969)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} promoted {member.mention} to {message}", color=0xFF6969)
        await utils.sendembed(ctx, e)

    @commands.command(name="noclip", description="Go rogue..")
    @commands.has_permissions(administrator=True)
    async def noclip(self, ctx):
        e = discord.Embed(
            description=f"{ctx.author.mention} is going rogue..", color=0xff0000)
        e.set_image(
            url=("https://c.tenor.com/xnQ97QtwQGkAAAAC/mm2roblox-fly-and-use-noclip.gif"))
        await utils.sendembed(ctx, e)

    @commands.command(name="abuse", description="Adbmind abuse!!")
    @commands.has_permissions(administrator=True)
    async def abuse(self, ctx, *, member: Optional[discord.Member]):
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} is going to abuse 😈", color=0xff0000)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} is going to abuse {member.mention} 😈", color=0xff0000)
        e.set_image(
            url=("https://i.pinimg.com/originals/e3/15/55/e31555da640e9f8afe59239ee1c2fc37.gif"))
        await utils.sendembed(ctx, e)
