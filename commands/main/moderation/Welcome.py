import sqlite3
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('./data/db/WelcomeMsg.db')
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS welcome_messages (
                    server_id INTEGER PRIMARY KEY,
                    welcome_message TEXT
                )
            ''')

    @commands.command(usage="<message>")
    async def welcomemsg(self, ctx, *, msg):
        """Set a custom welcome message. Ex. `!welcomemsg Welcome <user>!`"""
        server_id = ctx.guild.id
        with self.connection:
            self.connection.execute('''
                INSERT OR REPLACE INTO welcome_messages (server_id, welcome_message)
                VALUES (?, ?)
            ''', (server_id, msg))
        await ctx.send(f"Welcome message set to: {msg}")

    @commands.command(usage="!welcomeremove")
    async def welcomeremove(self, ctx):
        """Remove the set welcome message."""
        server_id = ctx.guild.id
        with self.connection:
            self.connection.execute('''
                DELETE FROM welcome_messages
                WHERE server_id = ?
            ''', (server_id,))
        await ctx.send("Welcome message removed.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send a welcome message when a new member joins."""
        server_id = member.guild.id
        with self.connection:
            cursor = self.connection.execute('''
                SELECT welcome_message
                FROM welcome_messages
                WHERE server_id = ?
            ''', (server_id,))
            row = cursor.fetchone()
            if row:
                welcome_message = row[0]
                customized_message = welcome_message.replace("<user>", member.mention)
                await member.guild.system_channel.send(customized_message)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
