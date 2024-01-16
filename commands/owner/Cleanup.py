import os
import json
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

        # Load file types from JSON file
        with open('./data/json/cleanupfiles.json', 'r') as file:
            file_types = json.load(file)

        deleted_files = 0
        for file_name in os.listdir('.'):
            if any(file_name.endswith(file_type) for file_type in file_types):
                os.remove(file_name)
                deleted_files += 1
        
        await ctx.send(f"Cleaned up and deleted {deleted_files} files.")

async def setup(bot):
    await bot.add_cog(Cleanup(bot))