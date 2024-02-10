import discord
from discord.ext import commands
import datetime
import sqlite3
import os

class Advertisement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_advertisement_database()
        self.server_names = {}
        self.bot.loop.create_task(self.collect_server_names())
        self.ads = []
        self.ad_index = {}

    async def collect_server_names(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            self.server_names[guild.id] = guild.name
        self.ads = self.load_ads()

    def initialize_advertisement_database(self):
        conn = sqlite3.connect('./data/db/advertisement.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ad_data (
                guild_id INTEGER PRIMARY KEY,
                command_count INTEGER,
                last_ad_time TEXT
            )
        """)
        conn.close()

    def get_ad_data_for_guild(self, guild_id):
        conn = sqlite3.connect('./data/db/advertisement.db')
        cursor = conn.cursor()
        cursor.execute("SELECT command_count, last_ad_time FROM ad_data WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        if result:
            return result[0], datetime.datetime.fromisoformat(result[1])
        else:
            cursor.execute("INSERT INTO ad_data (guild_id, command_count, last_ad_time) VALUES (?, 0, ?)", (guild_id, datetime.datetime.min.isoformat()))
            conn.commit()
            conn.close()
            return 0, datetime.datetime.min

    def save_ad_data_for_guild(self, guild_id, command_count, last_ad_time):
        conn = sqlite3.connect('./data/db/advertisement.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE ad_data SET command_count = ?, last_ad_time = ? WHERE guild_id = ?", (command_count, last_ad_time.isoformat(), guild_id))
        conn.commit()
        conn.close()

    def load_ads(self):
        ads = []
        ad_path = './data/txt/advertisement/'
        for filename in os.listdir(ad_path):
            if filename.endswith('.txt'):
                server_id = int(filename[:-4])  # Extract server ID from filename
                server_name = self.server_names.get(server_id, "Unknown Server")
                with open(os.path.join(ad_path, filename), 'r') as file:
                    ad_text = file.read().strip().replace("<server>", server_name)
                    ads.append(ad_text)
        return ads

    @commands.command()
    @commands.is_owner()  # Only allow the bot owner to use this command
    async def deletead(self, ctx, server_id: int):
        """Deletes the advertisement file for the specified server ID."""
        ad_path = f'./data/txt/advertisement/{server_id}.txt'
        if os.path.exists(ad_path):
            os.remove(ad_path)
            await ctx.send(f"Advertisement for server ID {server_id} deleted.")
        else:
            await ctx.send(f"No advertisement found for server ID {server_id}.")

    @commands.command()
    @commands.is_owner()  # Only allow the bot owner to use this command
    async def addad(self, ctx, server_id: int, *, ad_message: str):
        """Adds or updates the advertisement message for the specified server ID."""
        ad_path = f'./data/txt/advertisement/{server_id}.txt'
        with open(ad_path, 'w') as file:
            file.write(ad_message)
        await ctx.send(f"Advertisement for server ID {server_id} added/updated.")
        
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if not ctx.guild:  # Ignore DMs
            return

        guild_id = ctx.guild.id
        command_count, last_ad_time = self.get_ad_data_for_guild(guild_id)
        command_count += 1
        current_time = datetime.datetime.now()

        if command_count >= 50 or (current_time - last_ad_time) > datetime.timedelta(hours=12):
            await self.send_advertisement(ctx)
            command_count = 0
            last_ad_time = current_time

        self.save_ad_data_for_guild(guild_id, command_count, last_ad_time)

    async def send_advertisement(self, ctx):
        if not self.ads:  # Check if there are ads available
            print("No advertisements found.")
            return
    
        # Get the current ad index for this server, defaulting to 0
        guild_id = ctx.guild.id
        ad_index = self.ad_index.get(guild_id, 0)
    
        # Get the ad message
        ad_message = self.ads[ad_index]
    
        # Send the ad as an embed
        embed = discord.Embed(title="Advertisement", description=ad_message, color=discord.Color.blue())
        await ctx.channel.send(embed=embed)
    
        # Update the index for the next ad, looping back if at the end
        self.ad_index[guild_id] = (ad_index + 1) % len(self.ads)
            
    @commands.command()
    async def refresh_ads(self, ctx):
        """Admin command to refresh the advertisement list."""
        self.ads = self.load_ads()
        await ctx.send("Advertisement list refreshed.")

async def setup(bot):
    await bot.add_cog(Advertisement(bot))
