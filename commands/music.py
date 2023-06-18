import discord
from discord.ext import commands
import yt_dlp as ytdlp
import sqlite3
import os

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
        await self.play_next(guild_id)

        await ctx.send("Skipped to the next song in the queue.")

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
            self.db_curs.execute("DELETE FROM queue WHERE guild_id = ? AND song_url = ?",
                                 (guild_id, url))
            self.db_conn.commit()

        with ytdlp.YoutubeDL({'format': 'bestaudio/best', 'noplaylist':'True'}) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['entries'][0]['url'] if 'entries' in info else info['url']
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            voice.play(discord.FFmpegPCMAudio(URL, options="-vn"))
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

    async def play_next(self, guild_id):
        # The Context object isn't used in this case, so we just pass None
        await self.play(None, guild_id)

async def setup(bot):
    await bot.add_cog(Music(bot))
