from discord.ext import commands
from discord import Embed
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
                    embed = Embed(title=info['name'], description=info['summary'], color=0x3498db)
                    embed.add_field(name='Author', value=info['author'])
                    embed.add_field(name='Version', value=info['version'])
                    embed.add_field(name='License', value=info['license'])
                    embed.add_field(name='Package Home Page', value=info['package_url'])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Package not found.")

    @package_info.error
    async def package_info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument! Usage: `{ctx.prefix}package_info <package_name>`. This command is currently to get info about python packages!")
                
async def setup(bot):
    await bot.add_cog(Python(bot))
