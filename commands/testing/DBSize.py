import os
from discord.ext import commands
import discord

def get_directory_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    return total

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

class DBSize(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dbsize(self, ctx):
        """Retrieves the size of all .db files in the ./data directory."""
        embed = discord.Embed(title="Database Sizes", color=discord.Color.blue())
        
        for root, dirs, files in os.walk('./data'):
            for file in files:
                if file.endswith('.db'):
                    full_file_path = os.path.join(root, file)
                    file_size = get_directory_size(full_file_path)
                    file_size_readable = convert_size(file_size)
                    embed.add_field(name=full_file_path, value=file_size_readable, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DBSize(bot))
