from discord.ext import commands
import sqlite3
import re

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = './data/db/countingchannels.db'
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS counting_channels 
                          (channel_id INTEGER PRIMARY KEY, last_number INTEGER, last_user_id INTEGER)''')
        self.conn.commit()

    @commands.command(name='set_counting_channel', help='Sets the current channel as the counting channel.')
    async def set_counting_channel(self, ctx):
        channel_id = ctx.channel.id
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO counting_channels (channel_id, last_number, last_user_id) VALUES (?, 0, NULL)', (channel_id,))
        self.conn.commit()
        await ctx.send(f"Counting channel set to {ctx.channel.mention}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        cursor = self.conn.cursor()
        cursor.execute('SELECT last_number, last_user_id FROM counting_channels WHERE channel_id = ?', (channel_id,))
        row = cursor.fetchone()

        if row:
            last_number, last_user_id = row
            if message.author.id == last_user_id:
                await message.delete()
                return

            if re.match(r'^\d+$', message.content):
                number = int(message.content)
                if number == last_number + 1:
                    cursor.execute('UPDATE counting_channels SET last_number = ?, last_user_id = ? WHERE channel_id = ?', (number, message.author.id, channel_id))
                    self.conn.commit()
                    await message.add_reaction("✅")
                else:
                    await message.delete()

async def setup(bot):
    await bot.add_cog(Counting(bot))
