from discord.ext import commands
import logging

logger = logging.getLogger('Template.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/Template.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("Template Cog Loaded. Logging started...")

class Template(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Placeholder command
    @commands.command(usage="!placeholder <usage>", hidden=True) # Remove "hidden=True" for new commands 
    async def placeholder(self, ctx):
        """This is a placeholder command."""
        await ctx.send("This is a placeholder command. Replace it with your own implementation!")
        logger.info("Template command ran.")

async def setup(bot):
    await bot.add_cog(Template(bot))
