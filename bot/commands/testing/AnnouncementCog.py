import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class AnnouncementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announcement", description="Send an announcement to all default channels.")
    async def announcement(self, interaction: discord.Interaction, message: str):
        """Send an announcement to all default channels."""
        await interaction.response.send_message("Announcement is being sent to all servers. This may take some time.", ephemeral=True)
        
        for guild in self.bot.guilds:
            # Attempt to get the system channel or the first text channel
            channel = guild.system_channel or next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
            if channel:
                try:
                    await channel.send(message)
                except Exception as e:
                    print(f"Failed to send message to {guild.name}: {e}")
            
            # Add a delay between each message
            await asyncio.sleep(2)  # Adjust the delay as needed

async def setup(bot):
    await bot.add_cog(AnnouncementCog(bot))
