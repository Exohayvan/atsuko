import discord
from discord import app_commands
from discord.ext import commands
import logging
import requests  # Import requests

# Initialize logging
logger = logging.getLogger('FortniteBRStatsSync.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/FortniteBRStatsSync.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("Fortnite BR Stats Sync Cog Loaded. Logging started...")

class FortniteBRStats(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    group = app_commands.Group(name="fortnite", description="Commands related to Fortnite.")

    @group.command(name="stats", description="Get Fortnite BR stats for a player.")
    async def br_stats(self, interaction: discord.Interaction, username: str, account_type: str = 'epic', time_window: str = 'lifetime'):
        """ Fetches Fortnite BR player stats. """
        api_url = "https://fortnite-api.com/v2/stats/br/v2"
        headers = {
            "Authorization": "a571032c-b62d-4c76-9448-d5a521a06e0e"  # Replace with your actual API key
        }
        params = {
            "name": username,
            "accountType": account_type,
            "timeWindow": time_window
        }
        await interaction.response.defer()
        # Using the bot's event loop to run the blocking requests.get call in a separate thread
        data = await self.bot.loop.run_in_executor(None, lambda: requests.get(api_url, headers=headers, params=params))

        if data.status_code == 200:
            json_data = data.json()
            # Format the json_data as needed before sending
            await interaction.followup.send(f"Player BR Stats: {json_data}")
            logger.info(f"Fortnite BR stats retrieved for {username}.")
        else:
            await interaction.followup.send("Failed to retrieve BR stats.")
            logger.error(f"Failed to retrieve Fortnite BR stats for {username}.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FortniteBRStats(bot))