from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.volume = 1.0  # Default volume level

    @commands.command()
    async def join(self, ctx):
        """Joins the user's voice channel."""
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")
            return

        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()
        await ctx.send(f"I’ve joined {voice_channel.name}")

    @commands.command()
    async def leave(self, ctx):
        """Leaves the current voice channel."""
        if ctx.voice_client is None:
            await ctx.send("I'm not in a voice channel!")
            return

        channel_name = ctx.voice_client.channel.name
        await ctx.voice_client.disconnect()
        await ctx.send(f"Okay, goodbye for now, I’ve disconnected from {channel_name}")

    @commands.command()
    async def volume(self, ctx, volume: float):
        """Sets the volume of the bot."""
        if 0 <= volume <= 2:  # Limit volume between 0 and 2 for demonstration
            self.volume = volume
            await ctx.send(f"Volume set to {volume}!")
        else:
            await ctx.send("Volume must be between 0 and 2.")

async def setup(bot):
    await bot.add_cog(Music(bot))