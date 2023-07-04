from discord.ext import commands
import pip._internal.index as pip_index

class Python(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def package_info(self, ctx, package_name: str):
        """Provides information about a pip package."""
        try:
            package_finder = pip_index.PackageFinder()
            search_results = package_finder.find_requirement(package_name)
            if search_results:
                package = search_results[0]
                await ctx.send(f"Package: {package.name}\nSummary: {package.summary}")
            else:
                await ctx.send("Package not found.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Python(bot))