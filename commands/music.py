from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins the voice channel of the user who issued the command."""
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel!")
            return
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        """Leaves the voice channel of the guild if connected."""
        if not ctx.voice_client:
            await ctx.send("I am not connected to a voice channel!")
            return
        await ctx.voice_client.disconnect()

async def setup(bot):
    await bot.add_cog(Music(bot))
