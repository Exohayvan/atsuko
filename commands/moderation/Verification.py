import discord
from discord.ext import commands,tasks
import sqlite3
import random
from datetime import datetime, timedelta
from discord.ext.commands import MissingRequiredArgument
import logging
import os

# Create logs directory if it doesn't exist
if not os.path.exists('./logs'):
    os.makedirs('./logs')

logger = logging.getLogger('verification_bot')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/verification.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.info("Logging setup test message.")

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Database connection for roles
        self.conn = sqlite3.connect('./data/roles.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS roles
                     (guild_id INTEGER, join_role INTEGER, verify_role INTEGER)''')
        self.conn.commit()

        # Database connection for verification channels
        self.conn_verification_channel = sqlite3.connect('./data/verification_channel.db')
        self.c_verification_channel = self.conn_verification_channel.cursor()
        self.c_verification_channel.execute('''CREATE TABLE IF NOT EXISTS verification_channels
                     (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)''')
        self.conn_verification_channel.commit()

        # Database connection for verification time limit
        self.conn_verify_timelimit = sqlite3.connect('./data/verify_timelimit.db')
        self.c_verify_timelimit = self.conn_verify_timelimit.cursor()
        self.c_verify_timelimit.execute('''CREATE TABLE IF NOT EXISTS verify_timelimit
                     (guild_id INTEGER PRIMARY KEY, timelimit INTEGER)''')
        self.conn_verify_timelimit.commit()

        self.verification_dict = {}
        self.warned_users = {}  # Now maps (member_id, guild_id) to warning timestamp
        
    @commands.command(usage="!set_verify_timelimit <hours>")
    @commands.has_permissions(administrator=True)
    async def set_verify_timelimit(self, ctx, hours: int):
        """Sets a time limit for users to verify after joining."""
        self.c_verify_timelimit.execute("INSERT OR REPLACE INTO verify_timelimit VALUES (?, ?)", (ctx.guild.id, hours))
        self.conn_verify_timelimit.commit()
        await ctx.send(f"Verification time limit has been set to {hours} hours.")

    @commands.command(usage="!set_verify_channel <#channel>")
    @commands.has_permissions(administrator=True)
    async def set_verify_channel(self, ctx):
        """Sets a specific channel for verification purposes."""
        channel = ctx.channel
        self.c_verification_channel.execute("INSERT OR REPLACE INTO verification_channels VALUES (?, ?)", (ctx.guild.id, channel.id))
        self.conn_verification_channel.commit()
        await ctx.send(f"Verification channel has been set to {channel.mention}.")

    @commands.command(usage="!show_roles")
    @commands.has_permissions(administrator=True)
    async def show_roles(self, ctx):
        """Shows the set join and verify roles for the guild."""
        
        # Query the database for the roles
        self.c.execute("SELECT join_role, verify_role FROM roles WHERE guild_id=?", (ctx.guild.id,))
        roles = self.c.fetchone()
        
        # If we couldn't fetch the roles from the database
        if roles is None:
            await ctx.send("No entry found for this guild in the database.")
            return
    
        join_role, verify_role = roles
    
        # If either role ID is None, inform the user
        if join_role is None or verify_role is None:
            await ctx.send(f"Fetched roles from database:\nJoin Role ID: {join_role}\nVerify Role ID: {verify_role}")
            return
    
        join_role_obj = ctx.guild.get_role(join_role)
        verify_role_obj = ctx.guild.get_role(verify_role)
        
        # If we can't fetch the Role objects from the guild
        if join_role_obj is None or verify_role_obj is None:
            await ctx.send(f"One or both of the roles don't exist anymore in this server.\nJoin Role ID: {join_role}\nVerify Role ID: {verify_role}")
            return
    
        await ctx.send(f"Join Role: {join_role_obj.name}\nVerify Role: {verify_role_obj.name}")
        
    @commands.command(usage="!set_join_role <@role>")
    @commands.has_permissions(administrator=True)
    async def set_join_role(self, ctx, role: commands.RoleConverter):
        """Sets the role to give to users when they first join."""
        self.c.execute("INSERT OR REPLACE INTO roles VALUES (?, ?, (SELECT verify_role FROM roles WHERE guild_id=?))", (ctx.guild.id, role.id, ctx.guild.id))
        self.conn.commit()
        await ctx.send(f"Join role has been set to {role.name}.")
                
    @commands.command(usage="!set_verify_role <@role>")
    @commands.has_permissions(administrator=True)
    async def set_verify_role(self, ctx, role: commands.RoleConverter):
        """Sets the role to give to users when they are verified."""
        
        # Fetch the current join_role from the database
        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (ctx.guild.id,))
        join_role_id = self.c.fetchone()
        if join_role_id is None:  # If no record exists for the guild
            self.c.execute("INSERT INTO roles (guild_id, verify_role) VALUES (?, ?)", (ctx.guild.id, role.id))
        else:
            self.c.execute("UPDATE roles SET verify_role=? WHERE guild_id=?", (role.id, ctx.guild.id))
        
        self.conn.commit()
        await ctx.send(f"Verify role has been set to {role.name}.")
                
    @commands.command(usage="!verify")
    async def verify(self, ctx):
        """Sends a verification CAPTCHA to the user's DMs and alerts the user to check their DMs."""
        try:
            verification_number = random.randint(100, 999)
            self.verification_dict[ctx.author.id] = (verification_number, ctx.guild.id)
            await ctx.author.send(f"Please respond to this DM with this number to verify that you are a human: {verification_number}")
            await ctx.send(f"{ctx.author.mention}, I've sent you a DM with your verification number!", delete_after=60)
        except discord.Forbidden:
            # This exception is raised when the bot cannot send a DM to the user
            await ctx.send(f"{ctx.author.mention}, I couldn't send you a DM! Please open your DMs and try again.", delete_after=60)
        finally:
            # Delete the original command invocation message after 60 seconds
            await ctx.message.delete(delay=60)
            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return  # Skip the process for bots
        
        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (member.guild.id,))
        join_role_id = self.c.fetchone()
        if join_role_id is not None:
            join_role = member.guild.get_role(join_role_id[0])
            if join_role is not None:
                await member.add_roles(join_role)
            
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return
        # Ignore messages from users with administrator privileges
        if message.guild and message.author.guild_permissions.administrator:
            return

        # Handle messages in the verification channel
        if message.guild:  # Only proceed if the message is in a guild
            self.c_verification_channel.execute("SELECT channel_id FROM verification_channels WHERE guild_id=?", (message.guild.id,))
            result = self.c_verification_channel.fetchone()
            if result and message.channel.id == result[0]:  # Check if the message is in the verification channel
                if message.content.lower() not in ['!verify', '!accept_tos']:
                    reminder_msg = await message.channel.send(
                        f"{message.author.mention}, it looks like you are messaging in a verification channel. "
                        f"Please try the verify command.",
                        delete_after=60
                    )
                    await message.delete(delay=60)
                    return  # Return to prevent processing the message further
    
        # Handle verification CAPTCHA responses in direct messages
        if not message.guild:  # Check if the message is a DM
            verification_data = self.verification_dict.get(message.author.id)
    
            if verification_data and message.content.isdigit() and int(message.content) == verification_data[0]:
                await message.author.send("Verification successful!")
                
                guild = self.bot.get_guild(verification_data[1])
                if guild:
                    member = guild.get_member(message.author.id)
                    if member:
                        # Add the verify role
                        self.c.execute("SELECT verify_role FROM roles WHERE guild_id=?", (guild.id,))
                        verify_role_id = self.c.fetchone()
                        if verify_role_id:
                            verify_role = guild.get_role(verify_role_id[0])
                            if verify_role:
                                await member.add_roles(verify_role)
    
                        # Remove the join role
                        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (guild.id,))
                        join_role_id = self.c.fetchone()
                        if join_role_id:
                            join_role = guild.get_role(join_role_id[0])
                            if join_role:
                                await member.remove_roles(join_role)
    
                        self.verification_dict.pop(message.author.id, None)  # Remove used captcha
    
            elif verification_data:
                await message.author.send("Verification failed.")
                
    @tasks.loop(minutes=15)
    async def check_verification_timelimit(self):
        logger.info("Starting to check verification time limits.")
        try:
            self.c_verify_timelimit.execute("SELECT * FROM verify_timelimit")
            guilds_timelimits = self.c_verify_timelimit.fetchall()
        
            current_time = datetime.utcnow()
            to_remove = []
        
            for (member_id, guild_id), warning_time in self.warned_users.items():
                if current_time - warning_time >= timedelta(hours=1):
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        member = guild.get_member(member_id)
                        if member:
                            self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (guild_id,))
                            join_role_id = self.c.fetchone()
                            if join_role_id:
                                join_role = guild.get_role(join_role_id[0])
                                if join_role and join_role in member.roles:
                                    try:
                                        await guild.kick(member)
                                        logger.info(f"Kicked {member.display_name} from {guild.name} for not verifying in time.")
                                    except discord.Forbidden:
                                        logger.warning(f"Failed to kick {member.display_name} from {guild.name} due to insufficient permissions.")
                    to_remove.append((member_id, guild_id))
        
            for key in to_remove:
                del self.warned_users[key]
        
            for guild_id, timelimit in guilds_timelimits:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    logger.warning(f"Guild with ID {guild_id} not found.")
                    continue
        
                self.c_verification_channel.execute("SELECT channel_id FROM verification_channels WHERE guild_id=?", (guild_id,))
                verification_channel_id = self.c_verification_channel.fetchone()
                if not verification_channel_id:
                    logger.info(f"No verification channel set for guild ID {guild_id}.")
                    continue
                verification_channel = guild.get_channel(verification_channel_id[0])
        
                self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (guild_id,))
                join_role_id = self.c.fetchone()
                if not join_role_id:
                    logger.info(f"No join role set for guild ID {guild_id}.")
                    continue
                join_role = guild.get_role(join_role_id[0])
                if not join_role:
                    logger.warning(f"Join role with ID {join_role_id[0]} not found in guild {guild_id}.")
                    continue
        
                for member in guild.members:
                    if member.bot or join_role not in member.roles:
                        continue
                    if (member.id, guild_id) in self.warned_users:
                        continue
                    join_time = member.joined_at.replace(tzinfo=None)
                    if current_time - join_time > timedelta(hours=timelimit):
                        await self.warn_and_kick(member, guild, verification_channel, join_role, guild_id)
                        logger.info(f"Warning sent to {member.display_name} in {guild.name} for verification.")
        
        except Exception as e:
            logger.exception(f"An error occurred while checking verification time limits: {e}")    
        
    async def warn_and_kick(self, member, guild, verification_channel, join_role, guild_id):
        try:
            await member.send(f"You have 1 hour to verify in {guild.name} or you will be kicked.")
        except discord.Forbidden:
            # This exception is raised if the bot cannot send a DM to the user.
            pass
    
        warning_message = await verification_channel.send(f"{member.mention}, you have not verified within the set time limit. You have 1 hour to verify, or you will be kicked.")
    
        # Store the warning timestamp instead of waiting
        self.warned_users[(member.id, guild_id)] = datetime.utcnow()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready. Starting verification check task.")
        logger.info("Bot is ready. Starting verification check task.")
        self.check_verification_timelimit.start()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def trigger_time_test(self, ctx):
        try:
            logger.info("Manually triggering task logic for testing.")
            self.check_verification_timelimit.start()
        except Exception as e:
            logger.exception(f"Error during manual task trigger: {e}")
            
async def setup(bot):
    await bot.add_cog(Verification(bot))
