import discord
from discord.ext import commands, tasks
import os

class BadgeUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_badges.start()

    def cog_unload(self):
        self.update_badges.cancel()

    async def generate_badge_url(self, label, count, color='blue'):
        badge_url = f'https://img.shields.io/badge/{label}-{count}-{color}'
        return badge_url

    async def update_servers_txt(self):
        server_count = len(self.bot.guilds)
        with open('.github/badges/servers.txt', 'w') as file:
            file.write(str(server_count))
        badge_url = await self.generate_badge_url('Servers', server_count, 'green')
        with open('.github/badges/servers_badge_url.txt', 'w') as badge_file:
            badge_file.write(badge_url)

    async def update_users_txt(self):
        user_count = sum(len(guild.members) for guild in self.bot.guilds)
        with open('.github/badges/users.txt', 'w') as file:
            file.write(str(user_count))
        badge_url = await self.generate_badge_url('Users', user_count)
        with open('.github/badges/users_badge_url.txt', 'w') as badge_file:
            badge_file.write(badge_url)

    @tasks.loop(minutes=30)
    async def update_badges(self):
        await self.update_servers_txt()
        await self.update_users_txt()

    @update_badges.before_loop
    async def before_update_badges(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BadgeUpdater(bot))