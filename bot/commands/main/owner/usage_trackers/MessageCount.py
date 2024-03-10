import discord
from discord.ext import commands, tasks
import sqlite3
import os

class MessageCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        db_path = './data/db/messagecount.db'
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS message_counts(
                                user_id TEXT PRIMARY KEY,
                                count INT NOT NULL
                              )''')
        self.conn.commit()

        # Start the update file task
        self.update_message_count_file.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        user_id = str(message.author.id)
        self.cursor.execute('SELECT count FROM message_counts WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        if result:
            new_count = result[0] + 1
            self.cursor.execute('UPDATE message_counts SET count = ? WHERE user_id = ?', (new_count, user_id))
        else:
            self.cursor.execute('INSERT INTO message_counts (user_id, count) VALUES (?, ?)', (user_id, 1))
        self.conn.commit()

        # Optionally, you can call self.update_total_messages_file() here if you want to update the file immediately after each message.
        # However, consider the performance implications.

    async def update_total_messages_file(self):
        self.cursor.execute('SELECT SUM(count) FROM message_counts')
        total_messages = self.cursor.fetchone()[0]
        with open('./.github/badges/messagecount.txt', 'w') as file:
            file.write(str(total_messages))

    @tasks.loop(minutes=15)  # This task will now run every 15 minutes
    async def update_message_count_file(self):
        await self.update_total_messages_file()

    @update_message_count_file.before_loop
    async def before_update_message_count_file(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(MessageCount(bot))