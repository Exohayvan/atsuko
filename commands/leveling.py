from discord.ext import commands
import random
import sqlite3
import math

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('./data/xp.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, xp REAL, level INTEGER)")

    @commands.Cog.listener()
    async def on_message(self, message):
        if random.random() < 0.1: # 10% chance
            xp = len(message.content) * 0.1
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (message.author.id,))
            user = self.cursor.fetchone()
            if user is None: 
                self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (message.author.id, xp, 1))
            else:
                total_xp = user[1] + xp
                level = 1 + int(total_xp // 100)
                if level > user[2]:
                    await message.channel.send(f'Congratulations {message.author.name}, you have leveled up to level {level}!')
                self.cursor.execute("UPDATE users SET xp = ?, level = ? WHERE id = ?", (total_xp, level, message.author.id))
            self.db.commit()

    @commands.command()
    async def xp(self, ctx):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (ctx.author.id,))
        user = self.cursor.fetchone()
        if user is None:
            await ctx.send('You have no experience points.')
        else:
            xp_to_next_level = math.ceil(100 * (1.2 ** user[2])) - user[1]
            await ctx.send(f'You are level {user[2]}, with {user[1]} experience points. You need {xp_to_next_level} more XP to level up.')

async def setup(bot):
    await bot.add_cog(Leveling(bot))
