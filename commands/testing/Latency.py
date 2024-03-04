import discord
from discord.ext import commands, tasks
import aiosqlite
import os
import datetime

class Latency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_latency.start()

    def cog_unload(self):
        self.check_latency.cancel()

    async def create_db(self):
        async with aiosqlite.connect("./data/db/latency.db") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS latencies (
                                id INTEGER PRIMARY KEY,
                                timestamp DATETIME NOT NULL,
                                latency REAL NOT NULL)""")
            await db.commit()

    async def prune_db(self):
        two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)
        async with aiosqlite.connect("./data/db/latency.db") as db:
            await db.execute("DELETE FROM latencies WHERE timestamp < ?", (two_days_ago,))
            await db.commit()

    @tasks.loop(minutes=15)
    async def check_latency(self):
        await self.bot.wait_until_ready()
        latency = self.bot.latency  # Get the bot's latency to the Discord API

        # Ensure the database and table exist
        await self.create_db()

        # Insert the latency record
        async with aiosqlite.connect("./data/db/latency.db") as db:
            await db.execute("INSERT INTO latencies (timestamp, latency) VALUES (?, ?)",
                             (datetime.datetime.now(), latency))
            await db.commit()

        # Prune the database to keep only the last 2 days of data
        await self.prune_db()

        # Optionally, update the latency.txt file
        await self.update_latency_file(latency)

    async def update_latency_file(self, latency):
        os.makedirs("./.github/badges", exist_ok=True)
        with open("./.github/badges/latency.txt", "w") as f:
            f.write(f"Latest API Latency: {latency*1000:.2f}ms")

def setup(bot):
    bot.add_cog(Latency(bot))
