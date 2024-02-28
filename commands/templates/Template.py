from discord.ext import commands
import discord
import logging

# Initialize logging
logger = logging.getLogger('Template.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/Template.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("Template Cog Loaded. Logging started...")

class Template(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="placeholder", description="This is a placeholder command.")
    async def placeholder(self, interaction: discord.Interaction):
        """This is a placeholder slash command. Replace it with your own implementation!"""
        await interaction.response.send_message("This is a placeholder slash command. Replace it with your own implementation!")
        logger.info("Template slash command ran.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Template(bot))