import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
from datetime import datetime, timedelta

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
        # Calculate the start date for the query
        start_date = datetime.now() - timedelta(days=days)
        # Query to count 'online' and total records
        cursor.execute("""SELECT status, COUNT(*) FROM uptime_records
                          WHERE timestamp > datetime('now', ?)
                          GROUP BY status""", (f'-{days} days',))
        summary = cursor.fetchall()
        # Calculate the total possible checks (6 checks per hour)
        total_possible_checks = days * 24 * 6
        online_checks = sum(count for status, count in summary if status == 'online')
        connection.close()
        return online_checks, total_possible_checks

    @app_commands.command(name="uptime", description="Shows the bot's uptime summary.")
    async def uptime(self, interaction: discord.Interaction):
        message = "🕒 Uptime Summary:\n"
        for days in [1, 7, 30, 365]:
            online_checks, total_checks = await self.get_uptime_summary(days)
            percentage_online = (online_checks / total_checks) * 100 if total_checks else 0
            message += f"- Last {days} day(s): {percentage_online:.2f}% online ({online_checks}/{total_checks} checks)\n"
    
        await interaction.response.send_message(message)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Uptime(bot))
