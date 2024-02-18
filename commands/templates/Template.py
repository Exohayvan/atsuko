from discord.ext import commands

class Template(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Placeholder command
    @commands.command(usage="!placeholder <usage>", hidden=True) # Remove "hidden=True" for new commands 
    async def placeholder(self, ctx):
        """This is a placeholder command."""
        await ctx.send("This is a placeholder command. Replace it with your own implementation!")

async def setup(bot):
    await bot.add_cog(Template(bot))
