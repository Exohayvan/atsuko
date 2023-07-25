from discord import Embed
from discord.ext.commands import Greedy
from discord.ext import commands
import random
import sqlite3
import discord

XP_RATE = 2.2
CHANCE_RATE = 0.45
CHAR_XP = 0.1
START_CAP = 100 #not implemented

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('./data/db/xp.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, xp REAL, total_xp REAL, level INTEGER, level_xp REAL)")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.recalculate_levels()

    @commands.Cog.listener()
    async def on_message(self, message):
        EXCLUDED_SERVER_ID = 110373943822540800
        if message.author.bot:
            return
        xp = len(message.content) * CHAR_XP
        if random.random() < CHANCE_RATE:
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (message.author.id,))
            user = self.cursor.fetchone()
            if user is None:
                self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (message.author.id, xp, xp, 0, 100))
            else:
                total_xp = user[2] + xp
                remaining_xp = user[1] + xp
                level = user[3]
                level_xp = user[4]
                while remaining_xp >= level_xp:
                    remaining_xp -= level_xp
                    level += 1
                    level_xp = level_xp * XP_RATE
                    # Check if the message's guild ID is not the excluded one before sending the level-up message
                    if remaining_xp < level_xp and message.guild.id != EXCLUDED_SERVER_ID:
                        await message.channel.send(f'{message.author.mention} has leveled up to level {level}!')
                self.cursor.execute("UPDATE users SET xp = ?, total_xp = ?, level = ?, level_xp = ? WHERE id = ?", (remaining_xp, total_xp, level, level_xp, message.author.id))
            self.db.commit()

    @commands.command(usage="!xp` or `!xp @member")
    async def xp(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user.id,))
        user_data = self.cursor.fetchone()
        if user_data is None:
            await ctx.send(embed=discord.Embed(description=f'{user.mention} has no experience points.', color=0x00FFFF))
        else:
            xp_to_next_level = self.format_xp(user_data[4] - user_data[1])
            rounded_total_xp = self.format_xp(user_data[2])
            await ctx.send(embed=discord.Embed(description=f'{user.mention} is level {user_data[3]}, with {rounded_total_xp} total experience points. They need {xp_to_next_level} more XP to level up.', color=0x00FFFF))

    async def recalculate_levels(self):
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        for user in users:
            total_xp = user[2]
            level = 0
            next_level_xp = START_CAP
            while total_xp > next_level_xp:
                total_xp -= next_level_xp
                level += 1
                next_level_xp *= XP_RATE
            self.cursor.execute("UPDATE users SET xp = ?, level = ?, level_xp = ? WHERE id = ?", (total_xp, level, next_level_xp, user[0]))
        self.db.commit()

    @commands.command(usage="Bot Owner Command")
    async def removexp(self, ctx, user: discord.Member):
        if ctx.author.id == 276782057412362241:
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user.id,))
            self.db.commit()
            embed = Embed(description=f'XP for user {user.name} has been removed.', color=0x00FFFF)
            await ctx.send(embed=embed)

    def format_xp(self, amount):
        magnitude = 0
        while abs(amount) >= 1000:
            magnitude += 1
            amount /= 1000.0
        return '%.1f%s' % (amount, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

    @commands.command(usage="!leaderboard")
    async def leaderboard(self, ctx):
        self.cursor.execute("SELECT * FROM users ORDER BY total_xp DESC LIMIT 10")
        leaderboard = self.cursor.fetchall()
        embed = discord.Embed(title="XP Leaderboard", color=0x00FFFF)
        for i, user in enumerate(leaderboard, start=1):
            member = ctx.guild.get_member(user[0])
            if member is not None and not member.bot:
                formatted_xp = self.format_xp(user[2])  # use the function to format XP
                embed.add_field(name=f"{i}) {member.mention} | Level {user[3]} | Total XP {formatted_xp}", value='\u200b', inline=False)
        await ctx.send(embed=embed)

    @commands.command(usage="Bot Owner Command")
    async def rexp(self, ctx, *, user: str = None):
        if user is None:
            await ctx.send("Please provide a valid user or 'all'.")
        elif user.lower() == "all":
            await self.recalculate_levels()
            await ctx.send("Recalculated levels for all users.")
        else:
            try:
                member = await commands.MemberConverter().convert(ctx, user)
                self.cursor.execute("SELECT * FROM users WHERE id = ?", (member.id,))
                user_data = self.cursor.fetchone()
                if user_data is not None:
                    total_xp = user_data[2]
                    level = 0
                    next_level_xp = START_CAP
                    while total_xp > next_level_xp:
                        total_xp -= next_level_xp
                        level += 1
                        next_level_xp *= XP_RATE
                    self.cursor.execute("UPDATE users SET xp = ?, level = ?, level_xp = ? WHERE id = ?", (total_xp, level, next_level_xp, member.id))
                    self.db.commit()
                    await ctx.send(f"Recalculated level for {member.mention}. They are now at level {level} with {total_xp} XP remaining.")
                else:
                    await ctx.send(f"{member.mention} does not exist in the database.")
            except commands.BadArgument:
                await ctx.send("Invalid user. Please provide a valid user or 'all'.")
            
async def setup(bot):
    await bot.add_cog(Leveling(bot))
