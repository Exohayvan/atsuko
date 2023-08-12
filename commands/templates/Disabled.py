from discord.ext import commands

class Disabled(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="!disabled", name="disabled")
    async def _disabled(self, ctx):
        """This is a template for disabling a command!"""
        if 0 != 1:
            await ctx.send("This command is currently disabled.")
            return

    async def send_disabled_msg(self, ctx):
        await ctx.send("This command is currently disabled.")
        return
        
async def setup(bot):
    await bot.add_cog(Disabled(bot))
