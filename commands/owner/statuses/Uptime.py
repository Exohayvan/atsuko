import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
from datetime import datetime

class Uptime(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.database_path = './data/db/uptime.db'
        self.initialize_database()
        self.check_discord_connectivity.start()

    def cog_unload(self):
        self.check_discord_connectivity.cancel()

    def initialize_database(self):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS uptime_records (
                            id INTEGER PRIMARY KEY,
                            timestamp DATETIME NOT NULL,
                            status TEXT NOT NULL
                          );''')
        connection.commit()
        connection.close()

    async def record_uptime(self, status):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO uptime_records (timestamp, status) VALUES (?, ?)", (datetime.now(), status))
        connection.commit()
        connection.close()

    async def check_connectivity(self):
        try:
            await self.bot.fetch_user(self.bot.user.id)
            return "online"
        except Exception:
            return "offline"

    @tasks.loop(seconds=60)
    async def check_discord_connectivity(self):
        current_time = datetime.now()
        if current_time.minute % 10 == 0 and current_time.second < 5:  # A 5-second window for minor deviations
            status = await self.check_connectivity()
            await self.record_uptime(status)

    async def get_uptime_summary(self, days):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        cursor.execute("""SELECT status, COUNT(*) 
                          FROM uptime_records 
                          WHERE timestamp > datetime('now', ?) 
                          GROUP BY status""", (f'-{days} days',))
        summary = cursor.fetchall()
        connection.close()
        return summary

    @app_commands.command(name="uptime", description="Shows the bot's uptime summary.")
    async def uptime(self, interaction: discord.Interaction):
        uptime_1d = await self.get_uptime_summary(1)
        uptime_7d = await self.get_uptime_summary(7)
        uptime_30d = await self.get_uptime_summary(30)
        uptime_365d = await self.get_uptime_summary(365)

        message = f"🕒 Uptime Summary:\n"
        message += f"- Last 24 hours: {dict(uptime_1d).get('online', 0)} checks online\n"
        message += f"- Last 7 days: {dict(uptime_7d).get('online', 0)} checks online\n"
        message += f"- Last 30 days: {dict(uptime_30d).get('online', 0)} checks online\n"
        message += f"- Last 365 days: {dict(uptime_365d).get('online', 0)} checks online\n"

        await interaction.response.send_message(message)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Uptime(bot))
