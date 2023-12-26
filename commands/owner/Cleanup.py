import os
from discord.ext import commands

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def cleanup(self, ctx):
        # Check if the user's ID matches the allowed ID
        if ctx.author.id != 276782057412362241:
            return
        
        await ctx.send("Cleaning up...")

        deleted_files = 0
        for file_name in os.listdir('.'):
            if file_name.endswith('.png'):
                os.remove(file_name)
                deleted_files += 1
            if file_name.endswith('.gv'):
                os.remove(file_name)
                deleted_files += 1
        
        await ctx.send(f"Cleaned up and deleted {deleted_files} files.")

async def setup(bot):
    await bot.add_cog(Cleanup(bot))
