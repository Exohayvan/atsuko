import discord
from discord.ext import commands, tasks
import sqlite3
import os
import datetime
from functools import partial

class LatencyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_latency.start()
        self.db_path = "./data/db/latency.db"

    def cog_unload(self):
        self.check_latency.cancel()

    async def db_execute(self, query, *params):
        loop = self.bot.loop
        db_path = self.db_path
        def run():
            with sqlite3.connect(db_path) as conn:
                conn.execute(query, params)
                conn.commit()
        await loop.run_in_executor(None, run)

    async def create_db(self):
        await self.db_execute("""CREATE TABLE IF NOT EXISTS latencies (
                                  id INTEGER PRIMARY KEY,
                                  timestamp DATETIME NOT NULL,
                                  latency REAL NOT NULL)""")

    async def prune_db(self):
        two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)
        await self.db_execute("DELETE FROM latencies WHERE timestamp < ?", two_days_ago)

    @tasks.loop(minutes=15)
    async def check_latency(self):
        await self.bot.wait_until_ready()
        latency = self.bot.latency  # Get the bot's latency to the Discord API

        await self.create_db()
        await self.db_execute("INSERT INTO latencies (timestamp, latency) VALUES (?, ?)",
                              datetime.datetime.now(), latency)
        await self.prune_db()
        await self.update_latency_file(latency)

    async def update_latency_file(self, latency):
        os.makedirs("./.github/badges", exist_ok=True)
        with open("./.github/badges/latency.txt", "w") as f:
            f.write(f"Latest API Latency: {latency*1000:.2f}ms")

async def setup(bot):
    await bot.add_cog(LatencyCog(bot))
