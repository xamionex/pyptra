from typing import Optional
import discord
from discord.ext import commands, bridge
from cogs import block, utils
import random
# get image from url
import aiohttp
# image
from io import BytesIO
from petpetgif import petpet


def setup(bot):
    bot.add_cog(FunCommands(bot))


class FunCommands(commands.Cog, name="Fun"):
    """Commands you can use on other users for fun."""
    COG_EMOJI = "🚀"

    def __init__(self, ctx):
        self.ctx = ctx

    async def checkperm(self, ctx, perm):
        if await block.BlockCommands.get_perm(self, ctx, perm, ctx.author) or ctx.author.guild_permissions.administrator:
            return
        else:
            await utils.senderror(ctx, f"{ctx.author.mention}, You aren\'t allowed to use this")

    async def checkping(self, ctx, member):
        if await block.BlockCommands.get_perm(self, ctx, "ping", member):
            await utils.senderror(ctx, f"This person has disallowed me from using them in commands.")

    @bridge.bridge_command(name="pet")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pet(self, ctx, member: Optional[discord.member.Member], emoji: Optional[discord.PartialEmoji], url=None):
        """Pet someone :D"""
        await FunCommands.checkperm(self, ctx, "pet")
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
            disable = {'<', '>'}
            for key in disable.items():
                url = url.replace(key, '')
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

    @commands.command(hidden=True, name="hug")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hug(self, ctx, *, member: Optional[discord.Member]):
        """Hug someone :O"""
        await FunCommands.checkperm(self, ctx, "weird")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(self.ctx.hug_words_bot))} me!", color=0x0690FF)
        else:
            await self.checkping(ctx, member)
            e = discord.Embed(
                description=f"{ctx.author.mention} {(random.choice(self.ctx.hug_words))} {member.mention}", color=0x0690FF)
        e.set_image(url=(random.choice(self.ctx.hug_gifs)))
        await utils.sendembed(ctx, e)

    @commands.command(hidden=True, name="kiss")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def kiss(self, ctx, *, member: Optional[discord.Member]):
        """Kiss someone :O"""
        await FunCommands.checkperm(self, ctx, "weird")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(self.ctx.kiss_words_bot))} me!", color=0x0690FF)
        else:
            await self.checkping(ctx, member)
            e = discord.Embed(
                description=f"{ctx.author.mention} {(random.choice(self.ctx.kiss_words))} {member.mention}", color=0x0690FF)
        e.set_image(url=(random.choice(self.ctx.kiss_gifs)))
        await utils.sendembed(ctx, e)

    @commands.command(hidden=True, name="fall")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def fall(self, ctx, *, member: Optional[discord.Member]):
        """Make someone fall >:)"""
        await FunCommands.checkperm(self, ctx, "joke")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you fell", color=0xFF6969)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} made {member.mention} fall!", color=0xFF6969)
        e.set_thumbnail(url=(
            "https://media.discordapp.net/attachments/854984817862508565/883437876493307924/image0-2.gif"))
        await utils.sendembed(ctx, e)

    @commands.command(hidden=True, name="promote")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def promote(self, ctx, member: discord.Member, *, message=None):
        """Promote someone :D"""
        await FunCommands.checkperm(self, ctx, "joke")
        if member == ctx.author:
            e = discord.Embed(
                description=f"{ctx.author.mention} promoted themselves to {message}", color=0xFF6969)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} promoted {member.mention} to {message}", color=0xFF6969)
        await utils.sendembed(ctx, e)

    @commands.command(hidden=True, name="noclip")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def noclip(self, ctx):
        """Go rogue.."""
        e = discord.Embed(
            description=f"{ctx.author.mention} is going rogue..", color=0xff0000)
        e.set_image(
            url=("https://c.tenor.com/xnQ97QtwQGkAAAAC/mm2roblox-fly-and-use-noclip.gif"))
        await utils.sendembed(ctx, e)

    @commands.command(hidden=True, name="abuse")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def abuse(self, ctx, *, member: Optional[discord.Member]):
        """Adbmind abuse!!"""
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} is going to abuse 😈", color=0xff0000)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} is going to abuse {member.mention} 😈", color=0xff0000)
        e.set_image(
            url=("https://i.pinimg.com/originals/e3/15/55/e31555da640e9f8afe59239ee1c2fc37.gif"))
        await utils.sendembed(ctx, e)
