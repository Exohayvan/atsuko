import discord
from discord.ext import commands
import logging

# Setup logging
logger = logging.getLogger('Template.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/Template.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("Template Cog Loaded. Logging started...")

class Template(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Register the slash command to the bot's command tree
        self.bot.tree.add_command(self.placeholder)

    @discord.app_commands.command(name="placeholder", description="This is a placeholder command.")
    async def placeholder(self, interaction: discord.Interaction):
        """
        This is a placeholder slash command. Replace it with your own implementation!
        """
        await interaction.response.send_message("This is a placeholder slash command. Replace it with your own implementation!")
        logger.info("Template slash command ran.")

    # Make sure to remove the command when the cog is unloaded to prevent ghost commands
    def cog_unload(self):
        self.bot.tree.remove_command(self.placeholder.name, type=discord.AppCommandType.chat_input)

async def setup(bot):
    await bot.add_cog(Template(bot))
    # Synchronize the command tree to ensure the slash command is registered
    await bot.tree.sync()