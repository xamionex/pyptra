import textwrap
import requests
from PIL import Image, ImageDraw, ImageSequence, ImageFont
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

    @bridge.bridge_command(name="gif")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gif(self, ctx, member: Optional[discord.member.Member], emoji: Optional[discord.PartialEmoji], *, caption: str = None):
        """Make a caption on a gif"""
        msg = await ctx.respond("Creating...")
        dm = False
        if msg.channel.type == discord.ChannelType.private:
            dm = True
        elif not ctx.author.guild_permissions.manage_messages:
            await msg.delete()
            await utils.senderror(ctx, "You are missing Manage Messages permission(s) to run this command. (DM me to use this command freely.)")
            return
        caption = caption or "sample text"
        caption = utils.remove_newlines(caption)
        url = None
        if len(caption) > 1 and caption.startswith("http") or caption.startswith("<http"):
            caption = caption.split(" ")
            url = caption[0]
            caption = " ".join(caption[1:])
        elif len(caption) == 1 and caption.startswith("http") or caption.startswith("<http"):
            url = caption
            caption = "sample text"
        if len(caption) == 0:
            caption = "sample text"
        if url is not None:
            keys = ["<", ">"]
            for key in keys:
                url = url.replace(key, "")
        attachment = None
        try:
            attachment = ctx.message.attachments[0]
        except:
            pass
        image = member or emoji or attachment or url or ctx.author
        image, what = await FunCommands.get_url(self, ctx, image, dm)
        frames = FunCommands.set_frames(image, caption)
        # file-like container to hold the image in memory
        img = BytesIO()  # sets image as "img"
        # Save the frames as a new image
        frames[0].save(img, "gif", save_all=True, append_images=frames[1:])
        # set the file pointer back to the beginning so it doesn't upload a blank file.
        img.seek(0)
        file = discord.File(img, filename="caption.gif")
        e = discord.Embed(description=f"{ctx.author.mention} made a caption on {what}")
        e.set_image(url=f"attachment://caption.gif")
        if await utils.CheckInstance(ctx):
            await msg.edit(embed=e, file=file)
        else:
            await msg.edit_original_message(embed=e, file=file)

    @bridge.bridge_command(hidden=True, name="combinegif")
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def combine(self, ctx, link1, link2):
        """Combine two gifs"""
        link1 = utils.remove_newlines(link1)
        link2 = utils.remove_newlines(link2)
        keys = ["<", ">"]
        for key in keys:
            link1, link2 = link1.replace(key, ''), link2.replace(key, '')
        image1 = link1 or None
        image2 = link2 or None
        image1, what1 = await FunCommands.get_url(self, ctx, image1)
        image2, what2 = await FunCommands.get_url(self, ctx, image2)
        frames1 = FunCommands.set_frames(image1)
        frames2 = FunCommands.set_frames(image2)
        for i in range(len(frames1)):
            try:
                Image.Image.paste(frames1[i], frames2[i])
            except:
                break
        # file-like container to hold the image in memory
        img = BytesIO()  # sets image as "img"
        # Save the frames as a new image
        frames1[0].save(img, "png", save_all=True, append_images=frames1[1:])
        # set the file pointer back to the beginning so it doesn't upload a blank file.
        img.seek(0)
        file = discord.File(img, filename="combine.gif")
        e = discord.Embed(description=f"{ctx.author.mention} combined {what1} with {what2}")
        e.set_image(url=f"attachment://combine.gif")
        if await utils.CheckInstance(ctx):
            await ctx.respond(embed=e, file=file, mention_author=False)
        else:
            await ctx.respond(embed=e, file=file)

    @bridge.bridge_command(name="pet")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pet(self, ctx, member: Optional[discord.member.Member], emoji: Optional[discord.PartialEmoji], url=None):
        """Pet someone :D"""
        msg = await ctx.respond("Creating...")
        if msg.channel.type == discord.ChannelType.private:
            dm = True
        elif commands.has_permissions(manage_messages=True):
            dm = False
        caption = caption or "sample text"
        caption = utils.remove_newlines(caption)
        url = None
        if len(caption) > 1 and caption.startswith("http") or caption.startswith("<http"):
            caption = caption.split(" ")
            url = caption[0]
            caption = " ".join(caption[1:])
        elif len(caption) == 1 and caption.startswith("http") or caption.startswith("<http"):
            url = caption
            caption = "sample text"
        if len(caption) == 0:
            caption = "sample text"
        if url is not None:
            keys = ["<", ">"]
            for key in keys:
                url = url.replace(key, "")
        attachment = None
        try:
            attachment = ctx.message.attachments[0]
        except:
            pass
        image = member or emoji or attachment or url or ctx.author
        image, what = await FunCommands.get_url(self, ctx, image, dm)
        frames = FunCommands.set_frames(image, caption)
        # file-like container to hold the image in memory
        source = BytesIO()  # sets image as "source"
        # Save the frames as a new image
        frames[0].save(source, "gif", save_all=True, append_images=frames[1:])
        dest = BytesIO()  # container to store the petpet gif in memory
        # takes source (image) and makes pet-pet and puts into memory
        petpet.make(source, dest)
        # set the file pointer back to the beginning so it doesn't upload a blank file.
        dest.seek(0)
        file = discord.File(dest, filename="petpet.gif")
        e = discord.Embed(description=f"{ctx.author.mention} has pet {what}")
        e.set_image(url=f"attachment://petpet.gif")
        if await utils.CheckInstance(ctx):
            await msg.edit(embed=e, file=file)
        else:
            await msg.edit_original_message(embed=e, file=file)

    async def get_url(self, ctx, image, dm=False):
        # retrieve the image url
        what = "an image"
        if type(image) == discord.PartialEmoji:
            what = "an emoji"
            image = image.url
        elif type(image) == discord.Attachment:
            what = "an attachment"
            image = image.url
        elif type(image) == discord.member.Member or type(image) == discord.user.User:
            if not dm:
                await self.checkping(ctx, image)
            what = image.mention
            try:
                image = image.avatar.url
            except:
                await utils.senderror(ctx, "Could not get users avatar.")
        elif type(image) == str:
            async with aiohttp.ClientSession() as session:
                async with session.get(image) as url:
                    if url.status != 200:
                        await utils.senderror(ctx, "Could not download file")
                    image = url.url
                    await session.close()
        return image, what

    def set_frames(image: str, text=None):
        """get frames from gif (url) and apply text (if present)"""
        im = Image.open(requests.get(image, stream=True).raw)
        # A list of the frames to be outputted
        frames = []
        # Loop over each frame in the animated image
        for frame in ImageSequence.Iterator(im):
            # However, 'frame' is still the animated image with many frames
            # It has simply been seeked to a later frame
            # For our list of frames, we only want the current frame
            # Saving the image without 'save_all' will turn it into a single frame image, and we can then re-open it
            # To be efficient, we will save it to a buffer, rather than to file
            buffer_old, buffer_new = BytesIO(), BytesIO()
            frame.save(buffer_old, format="PNG")  # save current frame to 1st buffer
            if text is not None:
                editor = Editor(text, buffer_old)  # put old buffer through editor with text
            else:
                editor = Editor(None, buffer_old)  # put old buffer through editor without text
            img = editor.draw()  # user editor's draw func to get the finished result
            img = img.convert(mode='RGBA')
            img.save(buffer_new, "GIF", optimization=True, quality=80)  # Save with some image optimization # save finished result in new buffer
            frames.append(Image.open(buffer_new))  # Then append the single frame image to the list of frames
        return frames

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


class Editor:

    basewidth = 1200  # Width to make the editor
    fontBase = 100  # Font size
    letSpacing = 9  # Space between letters
    fill = (255, 255, 255)  # TextColor
    stroke_fill = (0, 0, 0)  # Color of the text outline
    lineSpacing = 10  # Space between lines
    stroke_width = 9  # How thick the outline of the text is
    fontfile = './data/impact.ttf'

    def __init__(self, caption, image):
        self.img = self.createImage(image)
        self.d = ImageDraw.Draw(self.img)
        self.caption = caption
        if caption:
            self.splitCaption = textwrap.wrap(caption, width=20)  # The text can be wider than the img. If thats the case split the text into multiple lines
            self.splitCaption.reverse()                           # Draw the lines of text from the bottom up

            fontSize = self.fontBase+10 if len(self.splitCaption) <= 1 else self.fontBase  # If there is only one line, make the text a bit larger
            self.font = ImageFont.truetype(font=self.fontfile, size=fontSize)
            # self.shadowFont = ImageFont.truetype(font='./impact.ttf', size=fontSize+10)

    def draw(self):
        '''
        Draws text onto this objects img object
        :return: A pillow image object with text drawn onto the image
        '''
        (iw, ih) = self.img.size
        if self.caption is not None:
            (_, th) = self.d.textsize(self.splitCaption[0], font=self.font)  # Height of the text
            y = (ih - (ih / 10)) - (th / 2)  # The starting y position to draw the last line of text. Text in drawn from the bottom line up

            for cap in self.splitCaption:  # For each line of text
                (tw, _) = self.d.textsize(cap, font=self.font)  # Getting the position of the text
                x = ((iw - tw) - (len(cap) * self.letSpacing))/2  # Center the text and account for the spacing between letters

                self.drawLine(x=x, y=y, caption=cap)
                y = y - th - self.lineSpacing  # Next block of text is higher up

        wpercent = ((self.basewidth/2) / float(self.img.size[0]))
        hsize = int((float(self.img.size[1]) * float(wpercent)))
        return self.img.resize((int(self.basewidth/2), hsize))

    def createImage(self, image):
        '''
        Resizes the image to a resonable standard size
        :param image: Path to an image file
        :return: A pil image object
        '''
        img = Image.open(image)
        wpercent = (self.basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        return img.resize((self.basewidth, hsize))

    def drawLine(self, x, y, caption):
        '''
        The text gets split into multiple lines if it is wider than the image. This function draws a single line
        :param x: The starting x coordinate of the text
        :param y: The starting y coordinate of the text
        :param caption: The text to write on the image
        :return: None
        '''
        for idx in range(0, len(caption)):  # For each letter in the line of text
            char = caption[idx]
            w, h = self.font.getsize(char)  # width and height of the letter
            self.d.text(
                (x, y),
                char,
                fill=self.fill,
                stroke_width=self.stroke_width,
                font=self.font,
                stroke_fill=self.stroke_fill
            )  # Drawing the text character by character. This way spacing can be added between letters
            x += w + self.letSpacing  # The next character must be drawn at an x position more to the right
