from discord.ext import commands

class Disabled(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="disabled")
    async def _disabled(self, ctx):
        if 0 != 1:
            await ctx.send("This command is currently disabled.")
            return

async def setup(bot):
    await bot.add_cog(Disabled(bot))
