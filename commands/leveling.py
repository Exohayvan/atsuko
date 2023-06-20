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
    async def xp(self, ctx):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (ctx.author.id,))
        user = self.cursor.fetchone()
        if user is None:
            embed = Embed(description='You have no experience points.', color=0x00FFFF)
            await ctx.send(embed=embed)
        else:
            xp_to_next_level = math.ceil(100 * (1.1 ** user[2])) - user[1]
            rounded_xp = round(user[1], 1)
            embed = Embed(description=f'You are level {user[2]}, with {rounded_xp} experience points. You need {xp_to_next_level} more XP to level up.', color=0x00FFFF)
            await ctx.send(embed=embed)

    @commands.command()
    async def removexp(self, ctx, user: discord.Member):
        if ctx.author.id == 276782057412362241:
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user.id,))
            self.db.commit()
            embed = Embed(description=f'XP for user {user.name} has been removed.', color=0x00FFFF)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))