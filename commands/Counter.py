import discord
from discord.ext import commands, tasks
import sqlite3
import os

class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_counters.start()

    def cog_unload(self):
        self.update_counters.cancel()

    @tasks.loop(minutes=10)  # Update every 10 minutes
    async def update_counters(self):
        guilds = self.bot.guilds
        conn = sqlite3.connect('./data/db/counter.db')
        c = conn.cursor()

        for guild in guilds:
            # Fetch the voice channels with the count from the database
            c.execute('SELECT channel_id FROM Counter WHERE guild_id = ?', (guild.id,))
            channel_ids = c.fetchall()
            
            for channel_id in channel_ids:
                channel = self.bot.get_channel(channel_id[0])
                if channel:
                    await self.update_counter(channel)

        conn.close()

    async def update_counter(self, channel):
        guild = channel.guild
        name = channel.name.split(':')[0]  # Get the part before the count

        if name == "Total members":
            count = len(guild.members)
        elif name == "Online members":
            count = len([member for member in guild.members if member.status != discord.Status.offline])
        elif name == "Bots":
            count = len([member.bot for member in guild.members if member.bot])

        await channel.edit(name=f'{name}: {count}')

    @commands.command(usage="!create_counter \"Counter Type\" (Must be inclosed in \"\". Also caps are needed. This is a bug will fix later.)")
    async def create_counter(self, ctx, name):
        """Creates a new counter voice channel with the given name. Counter types: Total members, Online members, Bots."""
        if name not in ["Total members", "Online members", "Bots"]:
            await ctx.send("Invalid counter name. Must be one of 'Total members', 'Online members', 'Bots'.")
            return

        channel = await ctx.guild.create_voice_channel(name + ": 0", category=ctx.channel.category)
        
        # Store the channel in the database
        conn = sqlite3.connect('./data/counter.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS Counter (guild_id int, channel_id int)')
        c.execute('INSERT INTO Counter VALUES (?, ?)', (ctx.guild.id, channel.id))
        conn.commit()
        conn.close()

        await self.update_counter(channel)

async def setup(bot):
    await bot.add_cog(Counter(bot))
