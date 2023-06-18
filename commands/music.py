import discord
from discord.ext import commands
import yt_dlp as ytdlp
import sqlite3
from yt_dlp.utils import DownloadError

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}

        self.db_conn = sqlite3.connect("./data/music_data.db")
        self.db_curs = self.db_conn.cursor()

        # Create tables if not exist
        self.db_curs.execute('''CREATE TABLE IF NOT EXISTS volume
                                (guild_id text PRIMARY KEY, volume integer)''')
        self.db_curs.execute('''CREATE TABLE IF NOT EXISTS queue
                                (guild_id text, song_url text)''')

        # Load the saved volume
        self.volume = {}
        self.db_curs.execute("SELECT * FROM volume")
        for guild_id, volume in self.db_curs.fetchall():
            self.volume[guild_id] = volume

    @commands.command()
    async def skip(self, ctx):
        guild_id = str(ctx.guild.id)

        # Stop the current song
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()

        # Start the next song
        await self.play_next(ctx)

        await ctx.send("Skipped to the next song in the queue.")

    @commands.command()
    async def volume(self, ctx, volume: int):
        # Check the volume is within a reasonable range
        if volume < 0 or volume > 100:
            await ctx.send("Volume must be between 0 and 100.")
            return

        # Save the volume
        self.volume[str(ctx.guild.id)] = volume
        self.db_curs.execute("INSERT OR REPLACE INTO volume VALUES (?, ?)",
                             (str(ctx.guild.id), volume))
        self.db_conn.commit()

        # Apply the volume to the current player, if any
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice is not None:
            voice.source.volume = volume / 100.0

        await ctx.send(f"Set volume to {volume}%.")

    @commands.command()
    async def clear(self, ctx):
        guild_id = str(ctx.guild.id)

        # Clear the queue for this server
        self.song_queue[guild_id] = []

        # Clear the queue in the database
        self.db_curs.execute("DELETE FROM queue WHERE guild_id = ?",
                             (guild_id,))
        self.db_conn.commit()

        await ctx.send("Cleared the song queue.")
        
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
    async def play(self, ctx, url: str = None):
        guild_id = str(ctx.guild.id)
        if not ctx.voice_client:
            await ctx.send("I am not connected to a voice channel!")
            return

        if url is None:  # If no url is provided, play from the queue
            self.db_curs.execute("SELECT song_url FROM queue WHERE guild_id = ? ORDER BY rowid ASC", (guild_id,))
            result = self.db_curs.fetchone()
            if result is None:
                await ctx.send("No more songs in the queue.")
                return
            url = result[0]

            # Remove the song from the queue in the database
            self.db_curs.execute("DELETE FROM queue WHERE guild_id = ? AND song_url = ?", (guild_id, url))
            self.db_conn.commit()

        await self.play_youtube(ctx, url)

    async def play_youtube(self, ctx, url):
        options = {
            'format': 'bestaudio/best',
            'noplaylist': 'True',
            'quiet': True
        }
        try:
            with ytdlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                URL = info['entries'][0]['url'] if 'entries' in info else info['url']
                voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
                audio_source = discord.FFmpegPCMAudio(URL, options="-vn")
                audio_source.volume = self.volume.get(str(ctx.guild.id), 100) / 100.0
                voice.play(audio_source)
        except DownloadError:
            await ctx.send("An error occurred while trying to play the song. This could be due to the video being private or not existing.")

    async def play_next(self, ctx):
        await self.play(ctx)

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
                