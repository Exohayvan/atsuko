import discord
from discord.ext import commands
import os

class BadgeUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_badges.start()

    def cog_unload(self):
        self.update_badges.cancel()

    async def generate_badge_url(self, file_path):
        try:
            with open(file_path, 'r') as file:
                count = file.read().strip()
                badge_url = f'https://img.shields.io/badge/Count-{count}-blue'
                return badge_url
        except FileNotFoundError:
            return None

    async def update_servers_txt(self):
        try:
            with open('.github/badges/servers.txt', 'r') as file:
                server_count = file.read().strip()
                badge_url = f'https://img.shields.io/badge/Servers-{server_count}-green'
                with open('.github/badges/servers_badge_url.txt', 'w') as badge_file:
                    badge_file.write(badge_url)
        except FileNotFoundError:
            pass

    async def update_users_txt(self):
        try:
            with open('.github/badges/users.txt', 'r') as file:
                user_count = file.read().strip()
                badge_url = f'https://img.shields.io/badge/Users-{user_count}-blue'
                with open('.github/badges/users_badge_url.txt', 'w') as badge_file:
                    badge_file.write(badge_url)
        except FileNotFoundError:
            pass

    @tasks.loop(minutes=30)
    async def update_badges(self):
        await self.update_servers_txt()
        await self.update_users_txt()

    @update_badges.before_loop
    async def before_update_badges(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BadgeUpdater(bot))