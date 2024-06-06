# cogs/tos.py

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
from datetime import datetime

class TOS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tos_message_id = None
        self.pending_commands = {}  # user_id: interaction
        self.initialize_tos_database()

    def initialize_tos_database(self):
        conn = sqlite3.connect('./data/db/tos.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS tos_accepted (user_id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

    async def has_accepted_tos(self, interaction: discord.Interaction):
        if interaction.command.name == "accept_tos":
            return True

        user_id = interaction.user.id

        conn = sqlite3.connect('./data/db/tos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM tos_accepted WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return True
        else:
            embed = discord.Embed(title="Terms of Service", description="You need to accept our Terms of Service before using this command.", color=discord.Color.red())
            embed.add_field(name="Read the TOS", value="[Click here to read the TOS](https://github.com/Exohayvan/atsuko/blob/main/documents/TOS.md)", inline=False)
            embed.add_field(name="Accept the TOS", value="React with ✅ or use `/accept_tos` to accept the Terms of Service.", inline=False)
            tos_message = await interaction.response.send_message(embed=embed, ephemeral=True)
            self.tos_message_id = tos_message.id

            self.pending_commands[user_id] = interaction

            # Schedule TOS message deletion after 60 seconds
            await asyncio.sleep(60)
            await tos_message.delete()

            return False

    @app_commands.command(name="accept_tos", description="Accept the Terms of Service")
    async def accept_tos(self, interaction: discord.Interaction):
        await self.accept_tos_procedure(interaction.user)
        await interaction.response.send_message("Thank you for accepting the Terms of Service!", ephemeral=True)

    async def accept_tos_procedure(self, user):
        user_id = user.id

        conn = sqlite3.connect('./data/db/tos.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO tos_accepted (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()

        if user_id in self.pending_commands:
            interaction = self.pending_commands[user_id]
            await self.bot.invoke(interaction)
            del self.pending_commands[user_id]

    @app_commands.command(name="tos_stats", description="Show TOS acceptance statistics")
    async def tos_stats(self, interaction: discord.Interaction):
        # Step 1: Count total number of unique users the bot can see
        total_users = set()  # Using a set to avoid counting duplicates
        for guild in self.bot.guilds:
            for member in guild.members:
                total_users.add(member.id)
        total_count = len(total_users)

        # Step 2: Count users who've accepted the TOS
        conn = sqlite3.connect('./data/db/tos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(user_id) FROM tos_accepted")
        accepted_count = cursor.fetchone()[0]
        conn.close()

        # Step 3: Compute the percentage
        if total_count > 0:
            accepted_percentage = (accepted_count / total_count) * 100
        else:
            accepted_percentage = 0

        # Send the stats
        embed = discord.Embed(title="TOS Acceptance Statistics", color=discord.Color.blue())
        embed.add_field(name="Total Users", value=str(total_count), inline=True)
        embed.add_field(name="Accepted TOS", value=str(accepted_count), inline=True)
        embed.add_field(name="Percentage Accepted", value=f"{accepted_percentage:.5f}%", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or str(reaction.emoji) != '✅':
            return

        if reaction.message.id == self.tos_message_id:
            await self.accept_tos_procedure(user)

async def setup(bot):
    await bot.add_cog(TOS(bot))
