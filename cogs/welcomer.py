import discord, asyncio, os, sys, time
from datetime import datetime, timedelta
from ordinal import ordinal
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageChops, ImageDraw, ImageFont
from io import BytesIO

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name = "hidden"

    # Code to round the Image (Profilepicture)
    def circle(pfp,size = (215,215)): 
        pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
        
        bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(pfp.size, Image.ANTIALIAS)
        mask = ImageChops.darker(mask, pfp.split()[-1])
        pfp.putalpha(mask)
        return pfp
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.bot.get_guild(1016377670348587058) # <- Your Server (Guild) ID (Right-Click on Server Icon -> Copy ID)
        text = guild.get_channel(1019359642251448330) # <- Your Welcome-Channel ID (Right-Click on Text-Channel -> Copy ID)

        welcome = discord.Embed(
            title = 'Welcome to Genius Invokation TCG!',
            description = f"""
╰・ Hey {member.mention}! We hope you enjoy your stay here! Please **read the rules** over at <#1019183031799525490> and check out <#1019186692575481978> to get started after verifying.

༉❀˚ Remember to keep a lookout for server-changes in our announcements channel over at <#1019186677039779921>!
""",
            color = 9455830
        )
        welcome.set_author(icon_url = member.avatar.url if member.avatar else self.bot.user.avatar, name=f"{member.name}#{member.discriminator} ({member.id})")
        welcome.set_thumbnail(url = member.avatar.url if member.avatar else self.bot.user.avatar)
        welcome.set_image(url = 'https://cdn.discordapp.com/attachments/1014919079154425917/1047206442203099246/cyno-genshin-impact-cyno.gif')
        welcome.set_footer(icon_url = self.bot.user.avatar, text = f"Genius Invokation TCG | {ordinal(self.bot.get_guild(1016377670348587058).member_count)} Traveler • Today at {(datetime.now()).strftime('%m/%d/%Y %I:%M:%S %p')} ")
        message = await text.send(embed = welcome)
        
async def setup(bot):
    await bot.add_cog(Welcomer(bot))