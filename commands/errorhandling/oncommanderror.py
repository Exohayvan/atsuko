from discord.ext import commands

class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(f'An error occurred: {str(error)}')

def setup(bot):
    bot.add_cog(ErrorHandling(bot))
