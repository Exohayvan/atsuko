from discord.ext import commands
import discord
import logging

# Setup logging as before
logger = logging.getLogger('WarningCog.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/WarningCog.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False

class WarningCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Warning Cog Loaded. Logging started...")

    @commands.command(name='warn', usage="!warn @user [reason]", help="Warns a user and deletes the warning command message.")
    @commands.has_permissions(manage_messages=True) # Ensure only users with the right permissions can use this command
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """Warns a user and deletes the command message."""
        await ctx.message.delete() # Delete the command message to clean up the chat
        warning_message = f"{member.mention}, you have been warned for: {reason}" if reason else f"{member.mention}, you have been warned."
        await ctx.send(warning_message)
        logger.info(f"Warn command used on {member} for '{reason}' by {ctx.author}.")

async def setup(bot):
    await bot.add_cog(WarningCog(bot))
    logger.info("WarningCog is loaded and ready.")
