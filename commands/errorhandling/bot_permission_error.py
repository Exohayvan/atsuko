from discord.ext import commands

class BotPermissionError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            missing_perms = error.missing_perms

            if "read_messages" in missing_perms or "send_messages" in missing_perms:
                # Ignore bot read/send message permissions errors
                return

            # Handle other missing permissions errors here
            await ctx.send("I'm sorry, I don't have the necessary permissions to execute that command.")

async def setup(bot):
    await bot.add_cog(BotPermissionError(bot))