import discord
from discord.ext import commands, tasks
import sqlite3

class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_counters.start()

    def cog_unload(self):
        self.update_counters.cancel()

    @tasks.loop(minutes=1)  # Reduced time for faster updates during testing
    async def update_counters(self):
        print("Updating counters")  # Debug log
        guilds = self.bot.guilds
        conn = sqlite3.connect('./data/db/counter.db')
        c = conn.cursor()

        for guild in guilds:
            print(f"Processing guild: {guild.id}")  # Log guild ID
            c.execute('SELECT channel_id FROM Counter WHERE guild_id = ?', (guild.id,))
            channel_ids = c.fetchall()

            for channel_id in channel_ids:
                print(f"Found channel ID in DB: {channel_id[0]}")  # Log channel ID from DB
                channel = self.bot.get_channel(channel_id[0])
                if channel:
                    print(f"Channel found: {channel.id}")  # Log fetched channel
                    await self.update_counter(channel)
                else:
                    print(f"Channel ID {channel_id[0]} not found, removing from DB")
                    c.execute('DELETE FROM Counter WHERE channel_id = ?', (channel_id[0],))

        conn.commit()
        conn.close()

    async def update_counter(self, channel):
        try:
            guild = channel.guild
            name = channel.name

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
                return  # If none of the keywords match, do nothing

            if channel.name != new_name:  # Only update if the name has changed
                await channel.edit(name=new_name)
                print(f"Updated channel: {channel.id} to {new_name}")  # Debug log

        except Exception as e:
            print(f"Error updating channel: {e}")  # Exception handling

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

    # Manual command to trigger counter update
    @commands.command(name='forceupdate')
    async def force_update(self, ctx):
        await self.update_counters()

async def setup(bot):
    await bot.add_cog(Counter(bot))