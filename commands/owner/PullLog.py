from discord.ext import commands
import discord
import os
import shutil
import logging

logger = logging.getLogger('PullLog')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/PullLog.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("PullLog Cog Loaded. Logging started...")

class PullLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_directory = './logs'
    
    @commands.command(usage="pulllog <filename>")
    async def pulllog(self, ctx, log_filename: str = None):
        """Send a log file or the entire log directory if no file is specified."""
        if log_filename:
            # Send specific log file
            file_path = os.path.join(self.log_directory, log_filename)
            if os.path.exists({file_path}):
                await ctx.send(file=discord.File(file_path))
                logger.info(f"Sent log file: {log_filename}")
            else:
                await ctx.send("Log file not found.")
                logger.error(f"Log file not found: {log_filename}")
        else:
            # Compress and send the entire log directory
            logger.info("Making log archive.")
            archive_path = shutil.make_archive("logs_backup", 'zip', self.log_directory)
            await ctx.send(file=discord.File(archive_path))
            logger.info("Sent compressed log directory.")
            os.remove(archive_path)  # Clean up the archive file after sending

async def setup(bot):
    await bot.add_cog(PullLog(bot))
