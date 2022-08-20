import re
from emoji import EMOJI_UNICODE
import textwrap
import requests
from PIL import Image, ImageDraw, ImageSequence, ImageFont
from pilmoji import Pilmoji
from typing import Final, Optional
import discord
from discord.ext import commands, bridge
from cogs.block import BlockCommands
from cogs.utils import Utils
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

    @bridge.bridge_command(name="gif")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gif(self, ctx, member: Optional[discord.member.Member], emoji: Optional[discord.PartialEmoji], *, caption: str = None):
        """Make a caption on a gif"""
        start_time = Utils.current_milli_time()
        self.msg = await ctx.respond("Trying to create...")
        dm = True if self.msg.channel.type == discord.ChannelType.private else False
        await BlockCommands.check_perm(self, ctx, "gif") if not dm else None
        what, frames, duration = await FunCommands.get_image(self, ctx, member, emoji, caption, dm)
        # file-like container to hold the image in memory
        img = BytesIO()  # sets image as "img"
        # Save the frames as a new image
        frames[0].save(img, "gif", save_all=True, append_images=frames[1:], duration=duration, loop=0)
        # set the file pointer back to the beginning so it doesn't upload a blank file.
        img.seek(0)
        file = discord.File(img, filename="caption.gif")
        e = discord.Embed(description=f"{ctx.author.mention} made a caption on {what}")
        e.set_image(url=f"attachment://caption.gif")
        if random.choice([1, 2]) > 1:
            e.set_footer(text="Protip: use pos=top (or center) before your text to display it at the top!")
        else:
            e.set_footer(text="Protip: you can enter a link before your text to use that instead!")
        counter = Utils.display_time(Utils.current_milli_time() - start_time)
        if await Utils.CheckInstance(ctx):
            await self.msg.edit(f"Done in {counter}", embed=e, file=file)
        else:
            await self.msg.edit_original_message(content=f"Done in {counter}", embed=e, file=file)

    @bridge.bridge_command(hidden=True, name="combinegif")
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def combine(self, ctx, link1, link2):
        """Combine two gifs"""
        link1 = Utils.remove_newlines(link1)
        link2 = Utils.remove_newlines(link2)
        keys = ["<", ">"]
        for key in keys:
            link1, link2 = link1.replace(key, ''), link2.replace(key, '')
        image1 = link1 or None
        image2 = link2 or None
        image1, what1 = await FunCommands.get_url(self, ctx, image1)
        image2, what2 = await FunCommands.get_url(self, ctx, image2)
        frames1 = await FunCommands.set_frames(self, ctx, image1)
        frames2 = await FunCommands.set_frames(self, ctx, image2)
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
        if await Utils.CheckInstance(ctx):
            await ctx.respond(embed=e, file=file, mention_author=False)
        else:
            await ctx.respond(embed=e, file=file)

    @bridge.bridge_command(name="pet")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pet(self, ctx, member: Optional[discord.member.Member], emoji: Optional[discord.PartialEmoji], *, caption: str = None):
        """Pet someone :D"""
        start_time = Utils.current_milli_time()
        self.msg = await ctx.respond("Trying to create...")
        dm = True if self.msg.channel.type == discord.ChannelType.private else False
        await BlockCommands.check_perm(self, ctx, "pet", self.msg) if not dm else None
        what, frames, duration = await FunCommands.get_image(self, ctx, member, emoji, caption, dm)
        source, dest = BytesIO(), BytesIO()  # sets image as "source" and container to store the petpet gif in memory
        frames[0].save(source, "gif", save_all=True, append_images=frames[1:], duration=duration, loop=0)  # Save the frames into source
        petpet.make(source, dest)  # takes source (image) and makes pet-pet and puts into memory
        dest.seek(0)  # set the file pointer back to the beginning so it doesn't upload a blank file.
        file = discord.File(dest, filename="petpet.gif")
        e = discord.Embed(description=f"{ctx.author.mention} has pet {what}")
        e.set_image(url=f"attachment://petpet.gif")
        counter = Utils.display_time(Utils.current_milli_time() - start_time)
        if await Utils.CheckInstance(ctx):
            await self.msg.edit(f"Done in {counter}", embed=e, file=file)
        else:
            await self.msg.edit_original_message(content=f"Done in {counter}", embed=e, file=file)

    async def get_image(self, ctx, member, emoji, caption, dm):
        caption, text, textposition, textcolor, url, attachment = await FunCommands.caption_args(self, ctx, caption)
        image = attachment or member or emoji or url or None
        image, what = await FunCommands.get_url(self, ctx, image, dm)
        if text:
            frames, duration = await FunCommands.set_frames(self, ctx, image, caption, textposition, textcolor)
        else:
            frames, duration = await FunCommands.set_frames(self, ctx, image)
        return what, frames, duration

    async def caption_args(self, ctx, caption):
        textposition, url, textcolor = None, None, None
        if caption is not None:
            keys = ["`", "\\"]
            for key in keys:
                caption = caption.replace(key, '')
            caption = Utils.remove_newlines(caption)
            caption = caption.split(" ")
            rem = []
            for item in caption:
                if item.startswith("pos="):
                    rem.append(item)
                    item = item.replace("pos=", "")
                    if item in Editor.trigs:
                        textposition = item
                if item.startswith("color="):
                    rem.append(item)
                    item = item.replace("color=", "")
                    for name, hx in Editor.colors.items():
                        if item == name:
                            textcolor = hx
            for trigger in ["http", "<http"]:
                for item in caption:
                    if trigger in item:
                        rem.append(item)
                        url = item
                        keys = ["<", ">"]
                        for key in keys:
                            url = url.replace(key, "")
                        break
                break
            for item in rem:
                caption.remove(item)
            caption = " ".join(caption[0:])
            if len(caption) > 0:
                text = True
            else:
                text = None
        else:
            text = None
        try:
            attachment = ctx.message.attachments[0]
        except:
            attachment = None
        return caption, text, textposition, textcolor, url, attachment

    async def get_url(self, ctx, image, dm=False):
        # retrieve the image url
        what = "an image"
        if image is None:
            ref = ctx.message.reference
            if ref is not None:
                ref = ref.cached_message
                try:
                    image = ref.attachments[0]
                except:
                    image = ref.author
            else:
                image = ctx.author.avatar.url
        if type(image) == discord.PartialEmoji:
            what = "an emoji"
            image = image.url
        elif type(image) == discord.Attachment:
            what = "an attachment"
            image = image.url
        elif type(image) == discord.member.Member or type(image) == discord.user.User:
            if not dm:
                await BlockCommands.check_ping(self, ctx, image, self.msg)
            what = image.mention if image.id != ctx.author.id else "themselves"
            try:
                image = image.avatar.url
            except:
                await Utils.send_error(ctx, "Could not get users avatar.", self.msg)
        elif type(image) == str:
            async with aiohttp.ClientSession() as session:
                async with session.get(image) as url:
                    if url.status != 200:
                        await Utils.send_error(ctx, "Could not download file", self.msg)
                    image = url.url
                    await session.close()
        return image, what

    async def set_frames(self, ctx, image: str, text=None, textposition=None, textcolor=None):
        """get frames from gif (url) and apply text (if present)"""
        if textposition is not None:
            if textposition not in ["top", "bottom", "center"]:
                await Utils.send_error(ctx, "Text position has to be either top bottom or center", self.msg)
        im = Image.open(requests.get(image, stream=True).raw)
        try:
            n_frames = im.frames
        except:
            n_frames = None
        if n_frames is not None:
            await Utils.send_error(ctx, f"Too many frames in gif. ({n_frames})", self.msg) if n_frames >= 60 else None
        # set the duration of the new gif to the same as the old one else 1 (because sometimes it's not a gif, so no duration)
        duration = [im.info['duration'] if 'duration' in im.info else 1][0]
        # A list of the frames to be outputted
        frames = []
        # Loop over each frame in the animated image
        for frame in ImageSequence.Iterator(im):
            # However, 'frame' is still the animated image with many frames
            # It has simply been seeked to a later frame
            # For our list of frames, we only want the current frame
            # Saving the image without 'save_all' will turn it into a single frame image, and we can then re-open it
            # To be efficient, we will save it to a buffer, rather than to file
            buffer = [BytesIO(), BytesIO()]
            # save current frame to 1st buffer
            frame.convert("RGBA").quantize(254, dither=Image.FLOYDSTEINBERG).save(buffer[0], format="PNG")
            # if text is used, add it, else skip text
            # then add the frame which is edited to the 2nd buffer
            [Editor(text, buffer[0], textposition, textcolor) if text is not None else Editor(None, buffer[0])][0].draw().save(buffer[1], "GIF")
            # finally add the finished frame from the 2nd buffer to the frame list
            frames.append(Image.open(buffer[1]))
        return frames, duration

    @commands.command(hidden=True, name="hug")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hug(self, ctx, *, member: Optional[discord.Member]):
        """Hug someone :O"""
        await BlockCommands.check_perm(self, ctx, "weird")
        if member == None:
            e = discord.Embed(description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(self.ctx.hug_words_bot))} me!", color=0x0690FF)
        else:
            await BlockCommands.check_ping(self, ctx, member)
            e = discord.Embed(description=f"{ctx.author.mention} {(random.choice(self.ctx.hug_words))} {member.mention}", color=0x0690FF)
        e.set_image(url=(random.choice(self.ctx.hug_gifs)))
        await ctx.respond(embed=e, mention_author=False)

    @commands.command(hidden=True, name="kiss")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def kiss(self, ctx, *, member: Optional[discord.Member]):
        """Kiss someone :O"""
        await BlockCommands.check_perm(self, ctx, "weird")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you didnt mention anyone but you can still {(random.choice(self.ctx.kiss_words_bot))} me!", color=0x0690FF)
        else:
            await BlockCommands.check_ping(self, ctx, member)
            e = discord.Embed(
                description=f"{ctx.author.mention} {(random.choice(self.ctx.kiss_words))} {member.mention}", color=0x0690FF)
        e.set_image(url=(random.choice(self.ctx.kiss_gifs)))
        await ctx.respond(embed=e, mention_author=False)

    @commands.command(hidden=True, name="fall")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def fall(self, ctx, *, member: Optional[discord.Member]):
        """Make someone fall >:)"""
        await BlockCommands.check_perm(self, ctx, "joke")
        if member == None:
            e = discord.Embed(
                description=f"{ctx.author.mention} you fell", color=0xFF6969)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} made {member.mention} fall!", color=0xFF6969)
        e.set_thumbnail(url=(
            "https://media.discordapp.net/attachments/854984817862508565/883437876493307924/image0-2.gif"))
        await ctx.respond(embed=e, mention_author=False)

    @commands.command(hidden=True, name="promote")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def promote(self, ctx, member: discord.Member, *, message=None):
        """Promote someone :D"""
        await BlockCommands.check_perm(self, ctx, "joke")
        if member == ctx.author:
            e = discord.Embed(
                description=f"{ctx.author.mention} promoted themselves to {message}", color=0xFF6969)
        else:
            e = discord.Embed(
                description=f"{ctx.author.mention} promoted {member.mention} to {message}", color=0xFF6969)
        await ctx.respond(embed=e, mention_author=False)

    @commands.command(hidden=True, name="noclip")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def noclip(self, ctx):
        """Go rogue.."""
        e = discord.Embed(
            description=f"{ctx.author.mention} is going rogue..", color=0xff0000)
        e.set_image(
            url=("https://c.tenor.com/xnQ97QtwQGkAAAAC/mm2roblox-fly-and-use-noclip.gif"))
        await ctx.respond(embed=e, mention_author=False)

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
        await ctx.respond(embed=e, mention_author=False)


class Editor:

    basewidth = 1200  # Width to make the editor
    fontBase = 100  # Font size
    letSpacing = 9  # Space between letters
    stroke_fill = (0, 0, 0)  # Color of the text outline
    lineSpacing = 10  # Space between lines
    stroke_width = 9  # How thick the outline of the text is
    #fontfile = './data/seguiemj.ttf'
    fontfile = "./data/fonts/arial-unicode-ms.ttf"
    trig_top = ["top"]
    trig_middle = ["center", "middle"]
    trigs = trig_top + trig_middle
    colors = {
        "blue": (0, 0, 255),
        "green": (0, 255, 0),
        "red": (255, 0, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "yellow": (255, 255, 0),
        "black": (1, 1, 1)
    }

    def __init__(self, caption, image, textposition=None, textcolor=(255, 255, 255)):
        self.img = self.createImage(image).convert("RGBA")
        self.d = ImageDraw.Draw(self.img)
        self.caption = caption
        self.txtpos = textposition
        self.fill = textcolor
        UNICODE_EMOJI_REGEX = '|'.join(map(re.escape, sorted(EMOJI_UNICODE['en'].values(), key=len, reverse=True)))
        DISCORD_EMOJI_REGEX = '<a?:[a-zA-Z0-9_]{2,32}:[0-9]{17,22}>'
        EMOJI_REGEX: Final[re.Pattern[str]] = re.compile(f'({UNICODE_EMOJI_REGEX}|{DISCORD_EMOJI_REGEX})')
        self.splitCaption, self.emojis = [], []
        if caption:
            for i, chunk in enumerate(EMOJI_REGEX.split(caption)):
                if not chunk or not i % 2:
                    [self.splitCaption.append(x) for x in textwrap.wrap(chunk, width=20)]
                else:
                    self.emojis.append(chunk)
                    self.splitCaption.append(chunk)
            [self.splitCaption.reverse() if textposition not in self.trigs else None]  # Draw the lines of text from the bottom up
            fontSize = self.fontBase+10 if len(self.splitCaption) <= 1 else self.fontBase  # If there is only one line, make the text a bit larger
            self.font = ImageFont.truetype(font=self.fontfile, size=fontSize, layout_engine=ImageFont.LAYOUT_RAQM, encoding="unic")
            #self.shadowFont = ImageFont.truetype(font=self.fontfile, size=fontSize+10, layout_engine=ImageFont.LAYOUT_RAQM, encoding="unic")

    def draw(self):
        '''
        Draws text onto this objects img object
        :return: A pillow image object with text drawn onto the image
        '''
        (iw, ih) = self.img.size
        if self.caption is not None:
            (_, th) = self.d.textsize(self.splitCaption[0], font=self.font)  # Height of the text
            if self.txtpos in self.trig_top:
                # y is (img height - img height/10) - (text height / 2)
                y = 20  # The starting y position to draw the last line of text. Text in drawn from the bottom line up
            elif self.txtpos in self.trig_middle:
                y = (ih - (ih / 2)) - (th / 2)  # The starting y position to draw the last line of text. Text in drawn from the bottom line up
            else:
                y = (ih - (ih / 10)) - (th / 2)  # The starting y position to draw the last line of text. Text in drawn from the bottom line up
            for cap in self.splitCaption:  # For each line of text
                (tw, _) = self.d.textsize(cap, font=self.font)  # Getting the position of the text
                x = ((iw - tw) - (len(cap) * self.letSpacing))/2  # Center the text and account for the spacing between letters
                if cap in self.emojis:
                    w, h = self.font.getsize("<")  # width and height of the letter
                    Pilmoji(self.img).text((int(x), int(y)), cap, font=self.font)  # Drawing the text character by character. This way spacing can be added between letters
                    x += w + self.letSpacing  # The next character must be drawn at an x position more to the right
                else:
                    self.drawLine(x=x, y=y, caption=cap)
                if self.txtpos in self.trig_top:
                    y = y + th + self.lineSpacing  # Next block of text is higher up
                elif self.txtpos in self.trig_middle:
                    y = y + th + self.lineSpacing  # Next block of text is higher up
                else:
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
            Pilmoji(self.img).text((int(x), int(y)), char, self.fill, self.font, stroke_width=self.stroke_width, stroke_fill=self.stroke_fill)  # Drawing the text character by character. This way spacing can be added between letters
            x += w + self.letSpacing  # The next character must be drawn at an x position more to the right
