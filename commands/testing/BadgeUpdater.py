import discord
from discord.ext import commands
import os

class BadgeUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def generate_badge_url(self):
        try:
            with open('.github/badges/servers.txt', 'r') as file:
                server_count = file.read().strip()
                badge_url = f'https://img.shields.io/badge/Servers-{server_count}-green'
                return badge_url
        except FileNotFoundError:
            return None

    @commands.command()
    async def show_server_count(self, ctx):
        badge_url = await self.generate_badge_url()
        if badge_url:
            await ctx.send(badge_url)
        else:
            await ctx.send("Server count not available.")

def setup(bot):
    bot.add_cog(BadgeUpdater(bot))