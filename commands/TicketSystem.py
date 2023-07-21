import discord
from discord.ext import commands
import sqlite3

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('data/db/tickets.db')
        self.cursor = self.conn.cursor()
        
        # Create the table if it doesn't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            guild_id INTEGER PRIMARY KEY,
            ticket_count INTEGER DEFAULT 1,
            channel_id INTEGER,
            user_id INTEGER
        )
        ''')
        self.conn.commit()

    @commands.command()
    async def ticket(self, ctx: commands.Context):
        """Create a new ticket channel."""
        
        # Retrieve the current ticket_count for the guild
        self.cursor.execute("SELECT ticket_count FROM tickets WHERE guild_id=?", (ctx.guild.id,))
        row = self.cursor.fetchone()
        
        if row:
            ticket_count = row[0] + 1
        else:
            ticket_count = 1
            self.cursor.execute("INSERT INTO tickets (guild_id) VALUES (?)", (ctx.guild.id,))

        channel_name = f"ticket-{ticket_count:03}"
        
        # Create a new text channel with the given name
        channel = await ctx.guild.create_text_channel(channel_name)
        
        # Store the channel ID and user ID in the database, and update the ticket_count
        self.cursor.execute('''
        UPDATE tickets SET ticket_count = ?, channel_id = ?, user_id = ? WHERE guild_id = ?
        ''', (ticket_count, channel.id, ctx.author.id, ctx.guild.id))
        
        self.conn.commit()

        await ctx.send(f"A new ticket channel named `{channel_name}` has been created!")

    def cog_unload(self):
        # Close the database connection when the cog is unloaded
        self.conn.close()

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
