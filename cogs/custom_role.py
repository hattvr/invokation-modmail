import discord
import asyncio
import traceback

from discord.app_commands import locale_str as _
from discord.ext import commands
from discord.ui import *

import urllib.parse
import urllib.request
    
from datetime import datetime
from typing import Union, Literal

from core import utils
from core.utils import trigger_typing
from core.models import (
    getLogger,
)
logger = getLogger(__name__)

def _embed(
    color: Literal["default", "error", "success", "plain", "gold"] = "default",
    title: str = "",
    message: str = "",
    thumbnail: str = None,
    footer: str = None,
    footer_img: str = None,
    author: str = None,
    author_img: str = None,
    image: str = None,
    timestamp: datetime = None,
    url: str = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=message,
        timestamp=timestamp,
        url=url,
        color={
            "default": discord.Color.blurple(),
            "error": discord.Color.brand_red(),
            "success": discord.Color.brand_green(),
            "gold": discord.Color.gold(),
            "plain": 3092790,
        }.get(color, discord.Color.blurple())
    )

    embed.set_thumbnail(url=thumbnail)
    embed.set_image(url=image)
    embed.set_footer(text=footer, icon_url=footer_img)
    if author:
        embed.set_author(name=author, icon_url=author_img)

    return embed

def is_image_url(url):
    # Check if the URL is valid
    try:
        result = urllib.parse.urlparse(url)
        if all([result.scheme, result.netloc]):
            return True
    except ValueError:
        return False

    # Check if the URL points to an image file
    try:
        response = urllib.request.urlopen(url)
        if response.headers.get_content_type().startswith('image/'):
            return True
    except:
        return False

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Premium Commands"

    async def get_custom_role_embed(
        self, _type: Union[commands.Context, discord.Interaction], user: int
    ) -> discord.Embed:
        user_settings = await self.bot.db.custom_role.find_one({"_id": user})

        embed = discord.Embed(
            title=f"Genius Invokation TCG Custom Role Settings",
            color=user_settings["color"] if (user_settings and user_settings["color"]) else discord.Color.purple(),
            timestamp=datetime.now(),
            description = f""" 
<:information:1034639378410115103> **Genius Invokation TCG Custom Role Settings**
Role Status: {f"`✅ Claimed`" if (user_settings and user_settings["id"]) else f"`❌ Unclaimed`"}
Role: {f"<@&{user_settings['id']}>" if (user_settings and user_settings["id"]) else f"`None`"}
Role Name: {user_settings["name"] if (user_settings and user_settings["name"]) else f"`None`"}
Role Color: `{f"`{user_settings['color']}`" if (user_settings and user_settings["color"]) else f"`Default`"}`"""
        )
        
        embed.set_footer(
            text="Genius Invokation TCG Custom Role", icon_url=self.bot.user.avatar
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar)

        return embed

    @commands.hybrid_command(
        name="role",
        description="Genius Invokation Custom Role Settings"
    )
    @utils.trigger_typing
    async def role(self, ctx: commands.Context) -> None:
        if not ctx.author.get_role(1060438448198127657):
            return await ctx.send("Not for you buddy ol pal")
            
        return await ctx.reply(
            embed=await self.get_custom_role_embed(ctx, ctx.author.id),
            view=CustomRoleView(ctx),
        )

class CustomRoleView(View):
    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.ctx = ctx

    @button(
        label="",
        style=discord.ButtonStyle.gray,
        emoji="<:information:1034639378410115103>",
    )
    async def custom_role_information(
        self, interaction: discord.Interaction, button: Button
    ):
        await interaction.response.defer()
        if self.ctx.author.id != interaction.user.id:
            return await interaction.followup.send(
                embed = _embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler! This **isn't your interaction** to touch!",
                ),
            )

        return await interaction.followup.send(
            embed=_embed(
                color="plain",
                message="<:information:1034639378410115103> Hey Traveler, as a **proud supporter** of Genius Invokation TCG, you'll have *exclusive* access to a custom role! You can change the name and color of your role at any time. You can also delete your custom role at any time. If you have any questions, please contact the **__support team__**.",
                thumbnail=interaction.client.user.avatar.url,
            ),
            ephemeral=True,
        )

    @button(label="Create Custom Role", style=discord.ButtonStyle.green, custom_id="CUSTOM_ROLE_CREATE_BUTTON")
    async def create_custom_role(
        self, interaction: discord.Interaction, button: Button
    ):
        await interaction.response.defer()
        if self.ctx.author.id != interaction.user.id:
            return await interaction.followup.send(
                embed = _embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler! This **isn't your interaction** to touch!",
                ),
            )

        check = await interaction.client.db.custom_role.find_one(
            {"_id": interaction.user.id}
        )
        if check and check["id"]:
            return await interaction.followup.send(
                embed=_embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler, you already have a custom role. If you would like to change it, please use the buttons below.",
                ),
                ephemeral=True,
            )

        role_name = f"{interaction.user.name}'s Custom Role"
        role = await interaction.guild.create_role(
            name=role_name,
            color=discord.Color.dark_teal(),
        )
        
        BASE_ROLE = interaction.guild.get_role(1060620018448080927)
        if BASE_ROLE:
            await role.edit(position = BASE_ROLE.position + 1)

        await interaction.user.add_roles(role)

        await interaction.client.db.custom_role.insert_one(
            {
                "_id": interaction.user.id,
                "id": role.id,
                "name": role_name,
                "color": None,
            }
        )

        await interaction.edit_original_response(
            embed=await interaction.client.get_cog("Premium").get_custom_role_embed(
                interaction, interaction.user.id
            )
        )

        return await interaction.followup.send(
            embed=_embed(
                color="success",
                message=f"<:yescheck:1021114525858136074> Successfully created custom role ({role.mention}). Please use the buttons below to change your unique role's name and color."
            ),
            ephemeral=True,
        )

    @button(label="Delete Custom Role", style=discord.ButtonStyle.danger, custom_id="CUSTOM_ROLE_DELETE_BUTTON")
    async def delete_custom_role(
        self, interaction: discord.Interaction, button: Button
    ):
        await interaction.response.defer()
        if self.ctx.author.id != interaction.user.id:
            return await interaction.followup.send(
                embed = _embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler! This **isn't your interaction** to touch!",
                ),
            )

        check = await interaction.client.db.custom_role.find_one({"_id": interaction.user.id})
        if not check or not check["id"]:
            return await interaction.followup.send(
                embed=_embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler, you don't have a custom role set up yet. Please create one first.",
                ),
                ephemeral=True,
            )

        await interaction.client.db.custom_role.delete_one({"_id": interaction.user.id})

        role = interaction.guild.get_role(check["id"])
        if role: await role.delete()

        await interaction.edit_original_response(
            embed=await interaction.client.get_cog("Premium").get_custom_role_embed(
                interaction, interaction.user.id
            )
        )

        return await interaction.followup.send(
            embed=_embed(
                color="success",
                message="<:yescheck:1021114525858136074> Your custom role has been successfully deleted.",
            ),
            ephemeral=True,
        )

    @button(label="Change Role Name", style=discord.ButtonStyle.gray, row=1, custom_id="CUSTOM_ROLE_NAME_CHANGE_BUTTON")
    async def custom_role_name(self, interaction: discord.Interaction, button: Button):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                embed = _embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler! This **isn't your interaction** to touch!",
                ),
            )

        check = await interaction.client.db.custom_role.find_one(
            {"_id": interaction.user.id}
        )
        if not check or not check["id"]:
            return await interaction.response.send_message(
                embed=_embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler, you don't have a custom role set up yet. Please create one first.",
                ),
                ephemeral=True,
            )

        await interaction.response.send_modal(CustomRoleModal(self.ctx, "Role"))

    @button(label="Change Role Color", style=discord.ButtonStyle.gray, row=1, custom_id="CUSTOM_ROLE_COLOR_CHANGE_BUTTON")
    async def custom_role_color(self, interaction: discord.Interaction, button: Button):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                embed = _embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler! This **isn't your interaction** to touch!",
                ),
            )

        check = await interaction.client.db.custom_role.find_one(
            {"_id": interaction.user.id}
        )
        if not check or not check["id"]:
            return await interaction.response.send_message(
                embed=_embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler, you don't have a custom role set up yet. Please create one first.",
                ),
                ephemeral=True,
            )

        await interaction.response.send_modal(CustomRoleModal(self.ctx, "Color"))

    @button(label="Change Role Icon", style=discord.ButtonStyle.gray, row=1, custom_id="CUSTOM_ROLE_ICON_CHANGE_BUTTON")
    async def custom_role_icon(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        if self.ctx.author.id != interaction.user.id:
            return await interaction.followup.send(
                embed = _embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler! This **isn't your interaction** to touch!",
                ),
            )

        check = await interaction.client.db.custom_role.find_one(
            {"_id": interaction.user.id}
        )
        if not check or not check["id"]:
            return await interaction.followup.send(
                embed=_embed(
                    color="error",
                    message="<:Error:1021889679857037372> Hey Traveler, you don't have a custom role set up yet. Please create one first.",
                ),
                ephemeral=True,
            )

        message = await interaction.followup.send(
            embed = _embed(
                color = "plain",
                message = "Please send the **link**, **attachment**, or **emoji** you want to use as your custom role icon. This request will time out in 60 seconds."
            )
        )
        
        try:
            msg = await interaction.client.wait_for(
                "message",
                check = lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel.id,
                timeout = 60
            )
        except asyncio.TimeoutError:
            return await message.edit(
                embed = _embed(
                    color = "error",
                    message = "<:Error:1021889679857037372> Hey Traveler! I didn't receive any input from you, so I've cancelled this request."
                )
            )

        try:
            if msg.attachments:
                if not msg.attachments[0].content_type.startswith("image/"):
                    return await message.edit(
                        embed = _embed(
                            color = "error",
                            message = "<:Error:1021889679857037372> Hey Traveler, the attachment must be an image!"
                        )
                    )
                icon = await msg.attachments[0].read() 
            elif msg.content.startswith("<") and msg.content.endswith(">"):
                partial_emoji = discord.PartialEmoji.from_str(msg.content)
                async with interaction.client.session.get(partial_emoji.url) as resp:
                    icon = await resp.read()
            elif is_image_url(msg.content):
                async with interaction.client.session.get(msg.content) as resp:
                    icon = await resp.read()
            else:
                icon = msg.content
            
            role = interaction.guild.get_role(check["id"])
            await role.edit(display_icon=icon)
            
            await message.edit(
                embed = _embed(
                    color = "success",
                    message = "<:yescheck:1021114525858136074> Your custom role icon has been successfully changed. This confirmation message will be deleted in **10 seconds**.",
                )
            )
            
            await asyncio.sleep(10)
            await msg.delete()
            await message.delete()
        except:
            logger.warning(traceback.format_exc())
        

class CustomRoleModal(Modal):
    def __init__(self, ctx: commands.Context, modal_type: str):
        super().__init__(
            title=f"Custom Role: {modal_type}"
        )
        self.ctx = ctx
        self.modal_type = modal_type

        find = self.ctx.bot.mongo.custom_role.find_one({"_id": self.ctx.author.id})
        self.role_id = find["id"]
        self.current_role = find["name"] if find["name"] else None
        self.current_color = find["color"] if find["color"] else None

        self.input = TextInput(
            label="Role Name" if modal_type == "Role" else "HEX Color Code",
            placeholder="Insert desired role name here..." if modal_type == "Role" else "#AF123AD...",
            default=(str(self.current_role)[:25] if self.current_role else None) if modal_type == "Role" else (self.current_color if self.current_color else None),
            style=discord.TextStyle.short,
            max_length=25 if modal_type == "Role" else 7,
            required=False,
        )

        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        role = interaction.guild.get_role(self.role_id)

        if self.modal_type == "Role":
            role_name = self.input.value

            await role.edit(name=role_name)

            await interaction.client.db.custom_role.update_one(
                {"_id": interaction.user.id}, {"$set": {"name": role_name}}
            )

            embed = await interaction.client.get_cog("Premium").get_custom_role_embed(
                interaction, interaction.user.id
            )
            await interaction.edit_original_response(embed=embed)

            return await interaction.followup.send(
                embed=discord.Embed(
                    color=self.current_color if self.current_color else discord.Color.dark_teal(),
                    description=f"<:yescheck:1021114525858136074> Role name changed to **{self.input.value}**."
                    ),
                    ephemeral=True,
                )

        elif self.modal_type == "Color":
            role_color = self.input.value

            if not role_color or "#" not in role_color:
                role_color = 3092790
            else:
                try:
                    role_color = int(role_color[1:], 16)
                except:
                    return await interaction.followup.send(
                        embed=_embed(
                            color="error",
                            message="I was unable to parse the HEX color code you provided. Please try again.",
                        ),
                        ephemeral=True,
                    )

            await role.edit(color=discord.Color(role_color))

            await interaction.client.db.custom_role.update_one(
                {"_id": interaction.user.id}, {"$set": {"color": role_color}}
            )

            embed = await interaction.client.get_cog("Premium").get_custom_role_embed(
                interaction, interaction.user.id
            )
            await interaction.edit_original_response(embed=embed)

            return await interaction.followup.send(
                embed=discord.Embed(
                    color=role_color,
                    description=f"<:yescheck:1021114525858136074> Role color changed to **#{self.input.value}**."
                ),
                ephemeral=True,
            )

async def setup(bot):
    await bot.add_cog(Premium(bot))
