from discord import Embed
from discord.ext.commands import Greedy
from discord.ext import commands
from discord import app_commands
import random
import sqlite3
import discord
import datetime
import logging

logger = logging.getLogger('Leveling.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/Leveling.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("Leveling Cog Loaded. Logging started...")

VOICE_XP_RATE = 12  # Set the XP awarded for every minute in a voice channel
active_voice_users = {}  # Store users and their join times
unnotified_users = {}

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
    async def on_voice_state_update(self, member, before, after):
        # If the member is a bot, ignore
        if member.bot:
            logger.info(f"Voice channel join: {member} is bot user, ignored")
            return
        try:
            # If the member joined a voice channel
            if after.channel and not before.channel:
                active_voice_users[member.id] = datetime.datetime.utcnow()
                logger.info(f"Voice channel join: {member} joined {after.channel.name}")
        
            # If the member left a voice channel
            elif before.channel and not after.channel:
                join_time = active_voice_users.pop(member.id, None)
                if join_time:
                    elapsed_minutes = (datetime.datetime.utcnow() - join_time).total_seconds() / 60
                    xp_earned = elapsed_minutes * VOICE_XP_RATE
                    await self.add_voice_xp(member, xp_earned)
                    logger.info(f"Voice channel leave: {member} left {before.channel.name}, earned {xp_earned} XP")
        except Exception as e:
            logger.error(f"Error in on_voice_state_update for {member}: {str(e)}")
    
    async def add_voice_xp(self, member, xp_earned):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (member.id,))
        user = self.cursor.fetchone()
        
        if user is None:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (member.id, xp_earned, xp_earned, 0, 100))
        else:
            total_xp = user[2] + xp_earned
            remaining_xp = user[1] + xp_earned
            level = user[3]
            level_xp = user[4]
            while remaining_xp >= level_xp:
                remaining_xp -= level_xp
                level += 1
                level_xp = level_xp * XP_RATE
                unnotified_users[member.id] = True  # Add this line
            self.cursor.execute("UPDATE users SET xp = ?, total_xp = ?, level = ?, level_xp = ? WHERE id = ?", (remaining_xp, total_xp, level, level_xp, member.id))
        self.db.commit()
    
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
                    if unnotified_users.get(message.author.id) or (remaining_xp < level_xp and message.guild.id != EXCLUDED_SERVER_ID):
                        await message.channel.send(f'{message.author.mention} has leveled up to level {level}!')
                        logger.info(f"{message.author.id} has leveled up to {level}")
                        unnotified_users.pop(message.author.id, None)  # Remove the user from the dictionary after notifying
                self.cursor.execute("UPDATE users SET xp = ?, total_xp = ?, level = ?, level_xp = ? WHERE id = ?", (remaining_xp, total_xp, level, level_xp, message.author.id))
            self.db.commit()

    @app_commands.command(name="xp", description="Check your own or someone else's XP and level.")
    async def xp(self, interaction: discord.Interaction, user: discord.Member = None):
        """Used to check your own or someone else's XP and level!"""
        if user is None:
            user = interaction.user
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user.id,))
        user_data = self.cursor.fetchone()
        if user_data is None:
            embed = discord.Embed(description=f'{user.mention} has no experience points.', color=0x00FFFF)
            await interaction.response.send_message(embed=embed)
        else:
            xp_to_next_level = self.format_xp(user_data[4] - user_data[1])
            rounded_total_xp = self.format_xp(user_data[2])
            embed = discord.Embed(description=f'{user.mention} is level {user_data[3]}, with {rounded_total_xp} total experience points. They need {xp_to_next_level} more XP to level up.', color=0x00FFFF)
            await interaction.response.send_message(embed=embed)
            
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

    def format_xp(self, amount):
        magnitude = 0
        while abs(amount) >= 1000:
            magnitude += 1
            amount /= 1000.0
        return '%.1f%s' % (amount, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

    @app_commands.command(name="leaderboard", description="Check the top 10 people in this server with my xp.")
    async def leaderboard(self, interaction: discord.Interaction):
        embed = discord.Embed(title="XP Leaderboard", color=0x00FFFF)
        
        valid_count = 0
        page = 0
        page_size = 100  # fetch more users initially as not all might be valid
    
        while valid_count < 10:
            offset = page * page_size
            self.cursor.execute("SELECT * FROM users ORDER BY total_xp DESC LIMIT ? OFFSET ?", (page_size, offset))
            users = self.cursor.fetchall()
    
            # If there are no more users to fetch, break out of the loop
            if not users:
                break
    
            # Fetch a batch of member IDs
            user_ids = [user[0] for user in users]
            members = []
            async for member in ctx.guild.fetch_members(limit=100):
                if member.id in user_ids:
                    members.append(member)
            
            member_dict = {member.id: member for member in members}    
            
            for user in users:
                member = member_dict.get(user[0])
                if member and not member.bot:
                    formatted_xp = self.format_xp(user[2])
                    embed.add_field(name=f"{valid_count + 1}) {member.mention} | Level {user[3]} | Total XP {formatted_xp}", value='\u200b', inline=False)
                    valid_count += 1
                    if valid_count >= 10:
                        break
    
            page += 1  # go to the next page of users
        
        await interaction.response.send_message(embed=embed)

    @commands.command(hidden=True)
    async def rexp(self, ctx, *, user: str = None):
        if ctx.message.author.id != 276782057412362241:
            await ctx.send("You don't have permission to use this command.")
            return
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
