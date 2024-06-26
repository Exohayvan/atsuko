import discord
from discord.ext import commands, tasks
import requests
import json
import asyncio

class TopGGCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQwNzkyOTQ4NjIwNjU2NjQwMCIsImJvdCI6dHJ1ZSwiaWF0IjoxNzA5MjY1NzUwfQ.Lr3WQMviNrJVEYBF3PpZDmVSJ11gOx6f-HVGI6Ghuzw'
        self.server_count_post.start()

    def cog_unload(self):
        self.server_count_post.cancel()

    def post_server_count(self):
        server_count = len(self.bot.guilds) if self.bot else 0  # Get the current server count if bot is not None
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'  # Specify JSON content type
        }
        payload = {
            'server_count': server_count
        }
        url = f"https://top.gg/api/bots/{self.bot.user.id}/stats"
        try:
            response = requests.post(url, headers=headers, json=payload)  # Use json parameter to send JSON data
            response.raise_for_status()  # Raise an error for non-200 status codes
            print('Server count posted successfully:', response.text)
        except requests.RequestException as e:
            print('Error posting server count:', e)
            print('Response content:', response.content)  # Print response content for debugging

    @tasks.loop(hours=6)  # Run every 6 hours
    async def server_count_post(self):
        if self.bot:  # Ensure bot is not None
            await self.bot.wait_until_ready()  # Ensure bot is ready
            self.post_server_count()  # Call the function to post server count

async def setup(bot):
    await bot.add_cog(TopGGCog(bot))
