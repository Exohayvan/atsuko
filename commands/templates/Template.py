import discord
from discord import app_commands
from discord.ext import commands
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
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
      
    @discord.app_commands.command(name="placeholder", description="This is a placeholder command.")
    async def placeholder(self, interaction: discord.Interaction):
        """This is a placeholder slash command. Replace it with your own implementation!"""
        await interaction.response.send_message("This is a placeholder slash command. Replace it with your own implementation!")
        logger.info("Template slash command ran.")
    
    group = app_commands.Group(name="parent", description="...")
    # Above, we declare a command Group, in discord terms this is a parent command
    # We define it within the class scope (not an instance scope) so we can use it as a decorator.
    # This does have namespace caveats but i don't believe they're worth outlining in our needs.

    @group.command(name="top-command")
    async def my_top_command(self, interaction: discord.Interaction) -> None:
        """ /top-command """
        await interaction.response.send_message("Hello from top level command!", ephemeral=True)

    @group.command(name="sub-command") # we use the declared group to make a command.
    async def my_sub_command(self, interaction: discord.Interaction) -> None:
        """ /parent sub-command """
        await interaction.response.send_message("Hello from the sub command!", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyCog(bot))
