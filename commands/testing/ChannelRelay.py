import discord
from discord.ext import commands, tasks
import datetime
import sqlite3

DATABASE_PATH = './data/db/channelrelays.db'

class ChannelRelay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_database()
        self.connected_channels = self.load_channels_from_db()
        self.last_message_times = self.load_last_message_times_from_db()
        self.safety_message = (
            "🔒 **Online Safety Reminder** 🔒\n\n"
            "- Always be cautious when sharing personal information. Avoid sharing your real name, address, phone number, or other identifiable details.\n"
            "- Remember that people online might not be who they say they are. Strangers can misrepresent themselves.\n"
            "- Never agree to meet someone you've only spoken to online without consulting a trusted adult. If you must meet, do so in a public place and bring a friend or family member.\n"
            "- Be wary of suspicious links or downloads. They could contain malware or phishing schemes.\n"
            "- If something or someone makes you uncomfortable, trust your instincts, and seek guidance from a trusted individual or report the behavior.\n"
            "- Remember to use strong and unique passwords for your online accounts. Avoid using easily guessable passwords like 'password123'.\n"
            "- It's okay to take breaks from online interactions. Your mental health and well-being are important.\n\n"
            "Stay safe and always prioritize your safety first!"
        )
        self.check_for_reminder.start()

    def setup_database(self):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS channels (guild_id INTEGER, channel_id INTEGER, UNIQUE(guild_id, channel_id))
            ''')
            conn.execute('''
            CREATE TABLE IF NOT EXISTS last_messages (channel_id INTEGER PRIMARY KEY, last_message_time TEXT)
            ''')

    def load_channels_from_db(self):
        with sqlite3.connect(DATABASE_PATH) as conn:
            return set(conn.execute('SELECT guild_id, channel_id FROM channels'))

    def load_last_message_times_from_db(self):
        with sqlite3.connect(DATABASE_PATH) as conn:
            return {row[0]: datetime.datetime.fromisoformat(row[1]) for row in conn.execute('SELECT channel_id, last_message_time FROM last_messages')}

    def add_channel_to_db(self, guild_id, channel_id):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('INSERT OR IGNORE INTO channels (guild_id, channel_id) VALUES (?, ?)', (guild_id, channel_id))

    def remove_channel_from_db(self, guild_id, channel_id):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('DELETE FROM channels WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))

    def update_last_message_time_in_db(self, channel_id, timestamp):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('INSERT OR REPLACE INTO last_messages (channel_id, last_message_time) VALUES (?, ?)', (channel_id, timestamp.isoformat()))

    @tasks.loop(minutes=1)
    async def check_for_reminder(self):
        for guild_id, channel_id in self.connected_channels:
            if channel_id in self.last_message_times:
                elapsed_time = datetime.datetime.now() - self.last_message_times[channel_id]
                if elapsed_time > datetime.timedelta(minutes=15):
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(self.safety_message)
                        del self.last_message_times[channel_id]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if (message.guild.id, message.channel.id) in self.connected_channels:
            self.last_message_times[message.channel.id] = datetime.datetime.now()
            self.update_last_message_time_in_db(message.channel.id, datetime.datetime.now())
            for guild_id, channel_id in self.connected_channels:
                if guild_id != message.guild.id or channel_id != message.channel.id:
                    target_guild = self.bot.get_guild(guild_id)
                    if target_guild:
                        target_channel = target_guild.get_channel(channel_id)
                        if target_channel:
                            await target_channel.send(f"{message.author.display_name}: {message.content}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def connect_channel(self, ctx, channel: discord.TextChannel=None):
        if not channel:
            channel = ctx.channel
        self.connected_channels.add((ctx.guild.id, channel.id))
        self.add_channel_to_db(ctx.guild.id, channel.id)
        await ctx.send(f"Connected {channel.mention} for relaying messages.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disconnect_channel(self, ctx, channel: discord.TextChannel=None):
        if not channel:
            channel = ctx.channel
        self.connected_channels.discard((ctx.guild.id, channel.id))
        self.remove_channel_from_db(ctx.guild.id, channel.id)
        await ctx.send(f"Disconnected {channel.mention} from relaying messages.")
    
    @commands.command()
    async def testcommand(self, ctx):
        await ctx.send("This is a test!")

async def setup(bot):
    await bot.add_cog(ChannelRelay(bot))