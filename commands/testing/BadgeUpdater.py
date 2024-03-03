import discord
from discord.ext import commands, tasks
import os
import asyncio

class BadgeUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_badges.start()

    def cog_unload(self):
        self.update_badges.cancel()

    async def update_servers_txt(self):
        print("Updating servers.txt")
        server_count = len(self.bot.guilds)
        with open('.github/badges/servers.txt', 'w') as file:
            file.write(str(server_count))

    async def update_users_txt(self):
        print("Updating users.txt")
        user_count = len(set(self.bot.get_all_members()))
        with open('.github/badges/users.txt', 'w') as file:
            file.write(str(user_count))

    @tasks.loop(minutes=30)
    async def update_badges(self):
        await self.update_servers_txt()
        await self.update_users_txt()

    @update_badges.before_loop
    async def before_update_badges(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    cog = BadgeUpdater(bot)
    await cog.before_update_badges()  # Ensure bot is ready before starting the loop
    await bot.add_cog(cog)
    print("BadgeUpdater cog added")