import discord
from discord.ext import commands, tasks
import sqlite3
import logging

logger = logging.getLogger('Counter.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/Counter.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.info("Counter Cog Loaded. Logging started...")

class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_counters.start()

    def cog_unload(self):
        self.update_counters.cancel()

    @tasks.loop(minutes=2)
    async def update_counters(self):
        logger.info("Updating counters")
        guilds = self.bot.guilds
        conn = sqlite3.connect('./data/db/counter.db')
        c = conn.cursor()
    
        for guild in guilds:
            logger.info(f"Processing guild: {guild.id}")
            c.execute('SELECT channel_id FROM Counter WHERE guild_id = ?', (guild.id,))
            channel_ids = c.fetchall()
    
            for channel_id in channel_ids:
                logger.info(f"Found channel ID in DB: {channel_id[0]}")
                channel = self.bot.get_channel(channel_id[0])
                if channel:
                    logger.info(f"Channel found: {channel.id}")
                    await self.update_counter(channel)
                else:
                    logger.info(f"Channel ID {channel_id[0]} not found, removing from DB")
                    # Delete the channel from the database if it can't be found
                    c.execute('DELETE FROM Counter WHERE channel_id = ?', (channel_id[0],))
    
        conn.commit()
        conn.close()

    async def update_counter(self, channel):
        try:
            guild = channel.guild
            name = channel.name
            logger.info(f"Updating counter for channel: {channel.id} in guild: {guild.id}")  # Log channel and guild

            if "Total members" in name:
                count = len(guild.members)
                new_name = f"Total members: {count}"
            elif "Online members" in name:
                count = len([member for member in guild.members if member.status != discord.Status.offline])
                new_name = f"Online members: {count}"
            elif "Bots" in name:
                count = len([member for member in guild.members if member.bot])
                new_name = f"Bots: {count}"
            else:
                logger.info("No matching counter type found.")  # Log if no match
                return  # If none of the keywords match, do nothing

            if channel.name != new_name:  # Only update if the name has changed
                await channel.edit(name=new_name)
                logger.info(f"Updated channel: {channel.id} to {new_name}")
            else:
                logger.info(f"No update needed for channel: {channel.id}")

        except Exception as e:
            logger.info(f"Error updating channel: {e}")  # Exception handling
            
    @commands.command()
    async def create_counter(self, ctx, *, name):
        """Creates a new counter voice channel with the given name. Counter types: Total members, Online members, Bots."""
        if name not in ["Total members", "Online members", "Bots"]:
            await ctx.send("Invalid counter name. Must be one of 'Total members', 'Online members', 'Bots'.")
            return

        channel = await ctx.guild.create_voice_channel(name + ": 0", category=ctx.channel.category)
        
        # Store the channel in the database
        conn = sqlite3.connect('./data/db/counter.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS Counter (guild_id int, channel_id int)')
        c.execute('INSERT INTO Counter VALUES (?, ?)', (ctx.guild.id, channel.id))
        conn.commit()
        conn.close()

        await self.update_counter(channel)

    @commands.command(name='channel_reconnect')
    async def channel_reconnect(self, ctx, channel: discord.VoiceChannel):
        """Reconnects a voice channel to the counter system and adds it back to the database."""
        # Check if the channel is already in the database
        conn = sqlite3.connect('./data/db/counter.db')
        c = conn.cursor()
        c.execute('SELECT * FROM Counter WHERE channel_id = ?', (channel.id,))
        if c.fetchone():
            await ctx.send("This channel is already connected.")
        else:
            # Add the channel back to the database
            c.execute('INSERT INTO Counter (guild_id, channel_id) VALUES (?, ?)', (ctx.guild.id, channel.id))
            conn.commit()
            conn.close()
            await ctx.send(f"Channel {channel.name} has been reconnected to the counter system.")
            await self.update_counter(channel)  # Optionally update the counter immediately
        
    # Manual command to trigger counter update
    @commands.command(name='channelupdate')
    async def channel_update(self, ctx):
        await self.update_counters()

async def setup(bot):
    await bot.add_cog(Counter(bot))
