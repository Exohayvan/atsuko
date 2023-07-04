from discord.ext import commands
import aiohttp

class Python(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def package_info(self, ctx, package_name: str):
        """Provides information about a pip package."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pypi.org/pypi/{package_name}/json') as r:
                if r.status == 200:
                    data = await r.json()
                    info = data['info']
                    await ctx.send(f"Package: {info['name']}\nSummary: {info['summary']}")
                else:
                    await ctx.send("Package not found.")
                    
async def setup(bot):
    await bot.add_cog(Python(bot))