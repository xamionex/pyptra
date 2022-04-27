from petpetgif import petpet
import discord
from discord.ext import commands
from io import BytesIO
from typing import Union, Optional

class FunCommands(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(name="pet", description="Pet someone :D")
    async def pet1(self, ctx, image: Optional[Union[discord.PartialEmoji, discord.member.Member]]):
        image = image or ctx.author
        e = await FunUtils.pet(ctx, image)
        await ctx.reply(embed=e[0], file=e[1], mention_author=False)

class FunUtils():
    async def pet(ctx, image):
        if type(image) == discord.PartialEmoji:
            image = await image.read() # retrieve the image bytes
            what = "an emoji"
        elif type(image) == discord.member.Member:
            what = image.mention
            image = await image.avatar.with_format('png').read() # retrieve the image bytes
        else:
            await ctx.reply('Please use a custom emoji or tag a member to petpet their avatar.')
            return

        source = BytesIO(image) # file-like container to hold the emoji in memory
        dest = BytesIO() # container to store the petpet gif in memory
        petpet.make(source, dest)
        dest.seek(0) # set the file pointer back to the beginning so it doesn't upload a blank file.
        filename = f"{image[0]}-petpet.gif"
        file = discord.File(dest, filename=filename)
        e = discord.Embed(description=f"{ctx.author.mention} has pet {what}")
        e.set_image(url=f"attachment://{filename}")
        return e, file