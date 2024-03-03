import discord
from discord.ext import commands
import sqlite3
import os

class MessageCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Ensure the database directory exists
        db_path = './data/db/messagecount.db'
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS message_counts(
                                user_id TEXT PRIMARY KEY,
                                count INT NOT NULL
                              )''')
        self.conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            # Don't count the bot's own messages
            return
        
        user_id = str(message.author.id)
        self.cursor.execute('SELECT count FROM message_counts WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        if result:
            # Update existing count
            new_count = result[0] + 1
            self.cursor.execute('UPDATE message_counts SET count = ? WHERE user_id = ?', (new_count, user_id))
        else:
            # Add new user with a count of 1
            self.cursor.execute('INSERT INTO message_counts (user_id, count) VALUES (?, ?)', (user_id, 1))
        self.conn.commit()

async def setup(bot):
    await bot.add_cog(MessageCount(bot))
