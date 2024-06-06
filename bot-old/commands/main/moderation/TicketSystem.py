import sqlite3
import discord
from discord.ext import commands

DATABASE_PATH = './data/db/tickets.db'
TICKETS_TABLE = 'tickets'
MOD_ROLE_DATABASE_PATH = './data/allowed_mods.db'  # Path to the Moderation cog's database

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TICKETS_TABLE} 
        (guild_id INTEGER PRIMARY KEY, ticket_count INTEGER, channel_id TEXT, user_id TEXT)
        ''')
        
        # Initialize connection to mod roles database
        self.mod_conn = sqlite3.connect(MOD_ROLE_DATABASE_PATH)
        self.mod_cursor = self.mod_conn.cursor()

    @commands.command(usage="!ticket")
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

        # Set permissions for the user who created the ticket
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True),
        }
        
        # Fetch mod roles from the database
        self.mod_cursor.execute("SELECT role_id FROM mod_roles WHERE guild_id=?", (ctx.guild.id,))
        mod_role_ids = [row[0] for row in self.mod_cursor.fetchall()]
        
        # Fetch the Role objects and set permissions
        for role_id in mod_role_ids:
            role = ctx.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)
        
        # Create a new text channel with the given name and the specified permissions
        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites)
        
        # Store the channel ID and user ID in the database, and update the ticket_count
        self.cursor.execute('''
        UPDATE tickets SET ticket_count = ?, channel_id = ?, user_id = ? WHERE guild_id = ?
        ''', (ticket_count, channel.id, ctx.author.id, ctx.guild.id))
        
        self.conn.commit()

        await ctx.send(f"A new ticket channel named `{channel_name}` has been created!")

    def cog_unload(self):
        # Close the database connections when the cog is unloaded
        self.conn.close()
        self.mod_conn.close()

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
