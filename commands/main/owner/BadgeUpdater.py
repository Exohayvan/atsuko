import discord
from discord.ext import commands, tasks
import os
from urllib.parse import quote

class BadgeUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_badges.start()

    def cog_unload(self):
        self.update_badges.cancel()

    async def generate_badge_url(self, label, message, color='blue'):
        # Ensure message is a string, especially if it's a numeric value like percentage
        message_str = str(message)

        adjusted_message = message_str.replace('%', '%25')
        # Encode the label and message to ensure the URL is valid
        
        badge_url = f'https://img.shields.io/badge/{label}-{adjusted_message}-{color}'
        return badge_url

    async def update_messagecount_txt(self):
        # Read the message count from the file
        messagecount_file_path = '.github/badges/messagecount.txt'
        try:
            with open(messagecount_file_path, 'r') as file:
                message_count = file.read().strip()
        except FileNotFoundError:
            print(f"File not found: {messagecount_file_path}")
            return  # Exit the method if the file doesn't exist

        # Generate the badge URL using the message count
        badge_url = await self.generate_badge_url('Messages_Processed', message_count, 'red')
        
        # Save the badge URL to a new file
        badge_url_file_path = '.github/badges/messagecount_badge_url.txt'
        with open(badge_url_file_path, 'w') as badge_file:
            badge_file.write(badge_url)
            
    async def update_uptime_badge_urls(self):
        # Define the periods for which to update uptime badge URLs
        periods = [1, 7, 30, 365]
        # Ensure the badges directory exists
        os.makedirs('.github/badges/', exist_ok=True)
        
        for period in periods:
            # Read the uptime percentage from the file
            uptime_file_path = f'.github/badges/{period}uptime.txt'
            try:
                with open(uptime_file_path, 'r') as file:
                    uptime_percentage = file.read().strip()
            except FileNotFoundError:
                print(f"File not found: {uptime_file_path}")
                continue  # Skip to the next period if the file doesn't exist

            # Generate the badge URL using the uptime percentage
            label = f'{period}Day_Uptime'
            badge_url = await self.generate_badge_url(label, uptime_percentage, 'blue')
            
            # Save the badge URL to a new file
            badge_url_file_path = f'.github/badges/{period}uptime_badge_url.txt'
            with open(badge_url_file_path, 'w') as badge_file:
                badge_file.write(badge_url)
                
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
        badge_url = await self.generate_badge_url('Users', user_count, 'yellow')
        with open('.github/badges/users_badge_url.txt', 'w') as badge_file:
            badge_file.write(badge_url)

    async def update_latency_txt(self):
        latency_file_path = '.github/badges/latency.txt'
        try:
            with open(latency_file_path, 'r') as file:
                latency = file.read().strip()
        except FileNotFoundError:
            print(f"File not found: {latency_file_path}")
            return
        badge_url = await self.generate_badge_url('API_Latency', latency, 'blue')
        with open('.github/badges/latency_badge_url.txt', 'w') as badge_file:
            badge_file.write(badge_url)
            
    @tasks.loop(minutes=10)
    async def update_badges(self):
        await self.update_servers_txt()
        await self.update_users_txt()
        await self.update_uptime_badge_urls()
        await self.update_messagecount_txt()
        await self.update_latency_txt()
        
    @update_badges.before_loop
    async def before_update_badges(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BadgeUpdater(bot))
