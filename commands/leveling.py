from discord import Embed
from discord.ext import commands
import random
import sqlite3
import math
import discord

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('./data/xp.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, xp REAL, level INTEGER)")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if random.random() < 0.1: # 10% chance
            xp = len(message.content) * 0.1
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (message.author.id,))
            user = self.cursor.fetchone()
            if user is None: 
                self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (message.author.id, xp, 1))
            else:
                total_xp = user[1] + xp
                if total_xp < 100:
                    level = 1
                else:
                    level = 1 + math.floor(math.log10(total_xp / 100) / math.log10(1.1))
                if level > user[2]:
                    embed = Embed(title="Level Up", description=f'Congratulations {message.author.name}, you have leveled up to level {level}!', color=0x00FFFF)
                    await message.channel.send(embed=embed)
                self.cursor.execute("UPDATE users SET xp = ?, level = ? WHERE id = ?", (total_xp, level, message.author.id))
            self.db.commit()

    @commands.command()
    async def xp(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user.id,))
        user_data = self.cursor.fetchone()
        if user_data is None:
            await ctx.send(embed=discord.Embed(description=f'{user.mention} has no experience points.', color=0x00FFFF))
        else:
            xp_to_next_level = math.ceil(100 * (1.1 ** user_data[2])) - user_data[1]
            rounded_xp = round(user_data[1], 1)
            await ctx.send(embed=discord.Embed(description=f'{user.mention} is level {user_data[2]}, with {rounded_xp} experience points. They need {xp_to_next_level} more XP to level up.', color=0x00FFFF))

    @commands.command()
    async def removexp(self, ctx, user: discord.Member):
        if ctx.author.id == 276782057412362241:
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user.id,))
            self.db.commit()
            embed = Embed(description=f'XP for user {user.name} has been removed.', color=0x00FFFF)
            await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        self.cursor.execute("SELECT * FROM users ORDER BY xp DESC LIMIT 10")
        leaderboard = self.cursor.fetchall()
        embed = discord.Embed(title="XP Leaderboard", color=0x00FFFF)
        for i, user in enumerate(leaderboard, start=1):
            member = ctx.guild.get_member(user[0])
            if member is not None and not member.bot:
                embed.add_field(name=f"{i}) {member.mention} | Level {user[2]} | XP {round(user[1], 1)}", value='\u200b', inline=False)
        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Leveling(bot))