import discord, time
from datetime import datetime
from discord.ext import commands
from discord import Webhook
from discord.ui import *
from io import BytesIO

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = None
        storage_webhook_url = "https://discord.com/api/webhooks/1053721913052119050/xltLqbiyoAAEULBdMhZ70WsVRnHMaTa6dF6qh9OtlrlST-RtG3PdOFk3Wu0DZbq-UnKy"
        self.storage_webhook = Webhook.from_url(storage_webhook_url, session = bot.session)
        self.name = "hidden"

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if 'custom_id' not in interaction.data:
            return

        if not self.log_channel:
            guild = await interaction.client.fetch_guild(1016377670348587058)
            self.log_channel = await guild.fetch_channel(1052339488283709461)
        
        if interaction.data['custom_id'] == "create_ticket":            
            await interaction.response.defer()
            
            support_category = interaction.channel.category
            ticket_channel = await support_category.create_text_channel(
                name = f"ticket-{interaction.user.display_name}",
                topic = f"{int(time.time())};{interaction.user.id};Not Claimed;Deck Submission",
                reason = f"Ticket created by {interaction.user} ({interaction.user.id})",
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True),
                    interaction.guild.get_role(1016382872074068028): discord.PermissionOverwrite(read_messages=True),
                    interaction.guild.get_role(1022936711417839657): discord.PermissionOverwrite(read_messages=True),
                    interaction.guild.get_role(1022936478449418240): discord.PermissionOverwrite(read_messages=True)
                }
            )
            
            fllw_up = discord.Embed(
                title = "Ticket Created",
                color = discord.Color.brand_green(),
                description = f"Your ticket has been created at {ticket_channel.mention}! Please be patient while we review your ticket."
            )
            fllw_up.set_image(url = 'https://cdn.discordapp.com/attachments/851450013031596063/912646733484425236/embed_divider.png')
            
            await interaction.followup.send(
                embed = fllw_up,
                ephemeral = True
            )
            
            response = discord.Embed(
                title = "Genius Invokation TCG Theorycrafting",
                description = f"""
**Please state the deck and characters you are submitting a guide for.**
<:information:1034639378410115103> You do not have to submit your guide *immediately*, but opening a ticket and not saying anything will lead to its closure. <a:ayakafan:1049215569213272126>""",
                color = 3092790
            )
            
            response.add_field(
                name = "**User Information**", value = f"""
> **User:** {interaction.user.mention}
> **Discord ID:** `{interaction.user.id}`
            """, inline = False
            )
            
            nview = discord.ui.View(timeout = None)
            nview.add_item(discord.ui.Button(label = "Close Ticket", style = discord.ButtonStyle.danger, custom_id = "close_ticket"))
            nview.add_item(discord.ui.Button(label = "Claim Ticket", style = discord.ButtonStyle.success, custom_id = "claim_ticket"))
            
            await ticket_channel.send(
                embed = response, 
                view = nview
            )
            
            mention_msg = await ticket_channel.send(f"{interaction.user.mention}")
            await mention_msg.delete()
            
            return
    
        elif interaction.data['custom_id'] == "close_ticket":
            await interaction.response.defer()
            
            response = discord.Embed(
                title = "Close Ticket - Confirmation",
                description = "Are you sure you want to close this ticket? This action is **irreversible**.",
                color = discord.Color.blurple()
            )
            
            nview = discord.ui.View()
            nview.add_item(discord.ui.Button(label = "Close Ticket", style = discord.ButtonStyle.blurple, custom_id = "tickets.close_yes"))
            nview.add_item(discord.ui.Button(label = "Cancel", style = discord.ButtonStyle.danger, custom_id = "tickets.close_no"))
            
            await interaction.followup.send(
                embed = response,
                view = nview
            )
        
            return
        elif interaction.data['custom_id'] == "claim_ticket":
            await interaction.response.defer()
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.followup.send(
                    embed = discord.Embed(
                        title = "Claim Ticket - Error",
                        description = "You do not have permission to claim tickets.",
                        color = discord.Color.red()
                    ),
                    ephemeral = True
                )
                return
            
            response = discord.Embed(
                title = "Claimed Ticket",
                description = f"Hey Traveler, your support ticket will be handled by {interaction.user.mention}.",
                color = discord.Color.blurple()
            )
            
            await interaction.channel.send(
                embed = response
            )
            
            nview = discord.ui.View(timeout = None)
            nview.add_item(discord.ui.Button(label = "Close Ticket", style = discord.ButtonStyle.danger, custom_id = "close_ticket"))
            
            await interaction.message.edit(view = nview)
            
            # update channel topic
            await interaction.channel.edit(
                topic = interaction.channel.topic.replace("Not Claimed", f"{interaction.user.id}")
            )
        
            return
        elif interaction.data['custom_id'] == "tickets.close_yes":
            await interaction.response.defer()
            
            
            
            messages, ticket_images = [], []
            async for message in interaction.channel.history(limit = None):
                if message.author.id == self.bot.user.id:
                    continue
                if message.attachments:
                    for attachment in message.attachments:
                        file = await attachment.to_file(
                            use_cached = True, 
                            spoiler = False
                        )
                        
                        delivered_msg = await self.storage_webhook.send(file = file, wait = True)
                        link = delivered_msg.attachments[0].url
                        ticket_images.append(link)
                
                messages.append(f"{message.author.display_name} ({message.author.id}): {message.content}\nImages: [{', '.join(ticket_images)}]")
            
            log = discord.Embed(
                title = "Ticket Closed",
                color = discord.Color.brand_green(),
                timestamp = datetime.now()
            )

            log_info = interaction.channel.topic.split(";")
            log.add_field(name = "Open Time", value = f"<t:{log_info[0]}:F>", inline = True)
            log.add_field(name = "Opened By", value = f"<@{log_info[1]}>", inline = True)
            log.add_field(name = "Closed By", value = interaction.user.mention, inline = True)
            log.add_field(name = "Close Time", value = f"<t:{int(time.time())}:F>", inline = True)
            log.add_field(name = "Claimed By", value = f"<@{log_info[2]}>" if log_info[2] != "Not Claimed" else log_info[3], inline = True)
            log.add_field(name = "Reason", value = f"```{log_info[3]}```", inline = False)
            log.set_footer(text = f"GITCG Support Log")
                
            await self.log_channel.send(
                embed = log,
                file = discord.File(
                    BytesIO("\n".join(messages).encode("utf-8")),
                    filename = f"{interaction.channel.name}.txt"
                ) if len(messages) > 0 else None
            )
            
            await interaction.channel.delete(
                reason = f"Ticket closed by {interaction.user} ({interaction.user.id})"
            )
            
            return
        elif interaction.data['custom_id'] == "tickets.close_no":
            await interaction.response.defer()
            await interaction.message.delete()
            
            return
        
class TicketButton(discord.ui.Button):
    """
    
    Button for creating a ticket
    
    """
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx

        super().__init__(
            label = "Create Deck Guide Submission Ticket", 
            style = discord.ButtonStyle.gray, 
            custom_id = f"create_ticket",
            emoji = "📩",
            row = 0
        )

async def setup(bot):
    await bot.add_cog(Tickets(bot))