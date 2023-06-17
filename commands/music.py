import discord
from discord.ext import commands
import yt_dlp as ytdlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []

    @commands.command()
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel!")
            return
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send("I am not connected to a voice channel!")
            return
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, url: str):
        if not ctx.voice_client:
            await ctx.send("I am not connected to a voice channel!")
            return
        with ytdlp.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            voice.play(discord.FFmpegPCMAudio(url2, options="-vn"))
            voice.is_playing()

    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("The audio is not paused.")

    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()

async def setup(bot):
    await bot.add_cog(Music(bot))
