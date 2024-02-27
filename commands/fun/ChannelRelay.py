import discord
from discord.ext import commands, tasks
import datetime
import sqlite3
import asyncio
from collections import defaultdict
import logging

logger = logging.getLogger('ChannelRelay.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/ChannelRelay.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("ChannelRelay Cog Loaded. Logging started...")

DATABASE_PATH = './data/db/channelrelays.db'

class ChannelRelay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_database()
        self.message_timestamps = defaultdict(list)
        self.message_counters = defaultdict(int)
        self.check_for_dynamic_slowmode.start()
        self.connected_channels = self.load_channels_from_db()
        self.last_message_times = self.load_last_message_times_from_db()
        self.unique_guilds_connected = len(set(guild_id for guild_id, _ in self.connected_channels))
        self.safety_message = (
            "🔒 **Online Safety Reminder** 🔒\n\n"
            "- Always be cautious when sharing personal information. Avoid sharing your real name, address, phone number, or other identifiable details.\n"
            "- Remember that people online might not be who they say they are. Strangers can misrepresent themselves.\n"
            "- Never agree to meet someone you've only spoken to online without consulting a trusted adult. If you must meet, do so in a public place and bring a friend or family member.\n"
            "- Be wary of suspicious links or downloads. They could contain malware or phishing schemes.\n"
            "- If something or someone makes you uncomfortable, trust your instincts, and seek guidance from a trusted individual or report the behavior.\n"
            "- Remember to use strong and unique passwords for your online accounts. Avoid using easily guessable passwords like 'password123'.\n"
            "- It's okay to take breaks from online interactions. Your mental health and well-being are important.\n\n"
            "❔**What is this channel** ❔\n"
            f"This channel is a relay or message portal to talk to other servers that have set this up.\n"
            f"Currently {self.unique_guilds_connected} servers have set this up.\n"
            "Anyone can set this up by using `connect_channel` so be cautious and please read the online safety."
        )
        self.user_last_message_time = defaultdict(lambda: defaultdict(lambda: datetime.datetime.min))
        self.is_bot_started = False
        self.check_for_reminder.start()

    def cog_unload(self):
        self.check_for_slowmode.cancel()
    
    def setup_database(self):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS channels (guild_id INTEGER, channel_id INTEGER, UNIQUE(guild_id, channel_id))
            ''')
            conn.execute('''
            CREATE TABLE IF NOT EXISTS last_messages (channel_id INTEGER PRIMARY KEY, last_message_time TEXT)
            ''')
            
    async def is_blacklisted(self, user_id):
        conn = sqlite3.connect('./data/db/blacklist.db')
        cursor = conn.cursor()
        cursor.execute("SELECT unban_timestamp FROM blacklist WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            unban_timestamp = datetime.fromtimestamp(result[0])
            if datetime.now() < unban_timestamp:
                return True
        return False
        
    def load_channels_from_db(self):
        with sqlite3.connect(DATABASE_PATH) as conn:
            return set(conn.execute('SELECT guild_id, channel_id FROM channels'))

    def load_last_message_times_from_db(self):
        with sqlite3.connect(DATABASE_PATH) as conn:
            return {row[0]: datetime.datetime.fromisoformat(row[1]) for row in conn.execute('SELECT channel_id, last_message_time FROM last_messages')}

    def add_channel_to_db(self, guild_id, channel_id):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('INSERT OR IGNORE INTO channels (guild_id, channel_id) VALUES (?, ?)', (guild_id, channel_id))

    def remove_channel_from_db(self, guild_id, channel_id):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('DELETE FROM channels WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))

    def update_last_message_time_in_db(self, channel_id, timestamp):
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('INSERT OR REPLACE INTO last_messages (channel_id, last_message_time) VALUES (?, ?)', (channel_id, timestamp.isoformat()))

    @staticmethod
    def get_cooldown_emoji(cooldown):
        if cooldown == 0:
            return "✅"  # Green check for no slowmode
        elif 1 <= cooldown <= 20:
            return "⚠️"  # Warning triangle for short cooldowns
        elif 21 <= cooldown <= 60:
            return "❗"  # Exclamation mark for slightly longer cooldowns
        elif 61 <= cooldown <= 300:  # 1 to 5 minutes
            return "🟡"  # Yellow circle indicating caution as we get into minutes
        elif 301 <= cooldown <= 900:  # 5 to 15 minutes
            return "🟠"  # Orange circle for medium cooldowns
        elif 901 <= cooldown <= 3600:  # 15 minutes to 1 hour
            return "🔴"  # Red circle for high cooldowns
        elif 3601 <= cooldown <= 21600:  # 1 hour to 6 hours (MAX_SLOWMODE)
            return "⛔"  # No entry sign for very long cooldowns
        else:
            return "❓"  # default case, should not normally happen
        
    @tasks.loop(seconds=1)  # Adjust time as needed
    async def check_for_dynamic_slowmode(self):
        logger.info("Checking if slowmode is needed.")
        # Prune messages older than 15 minutes from all channels first
        fifteen_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=15)
        for channel_id in self.message_timestamps:
            self.message_timestamps[channel_id] = [timestamp for timestamp in self.message_timestamps[channel_id] if timestamp > fifteen_mins_ago]
        MAX_SLOWMODE = 21600  # Discord's maximum slowmode is 6 hours or 21600 seconds
        POWER = 3.3  # Adjust this value to control the growth rate. 2 is quadratic, 3 is cubic, etc.
    
        for guild_id, channel_id in self.connected_channels:
            channel = self.bot.get_channel(channel_id)
            if channel:
                # Calculate messages per minute
                messages_last_15_minutes = len(self.message_timestamps[channel_id])
                messages_per_minute = messages_last_15_minutes / 15
    
                # Calculate cooldown using messages per minute with power
                if messages_per_minute == 0:
                    cooldown = 0
                else:
                    logger.warning("Slowmode needed. Calulating cooldown limit.")
                    fraction = messages_per_minute / 60  # Assuming a potential max of 60 messages per minute
                    cooldown = int(MAX_SLOWMODE * fraction**POWER)
                    cooldown = min(cooldown, MAX_SLOWMODE)  # Ensure cooldown doesn't exceed max limit
    
                # Check and update the cooldown even if it's the same, to ensure dynamic updating
                if channel.slowmode_delay != cooldown:
                    try:
                        await channel.edit(slowmode_delay=cooldown)
                        emoji = ChannelRelay.get_cooldown_emoji(cooldown)
                        logger.warning(f"Slowmode enabled and set to {cooldown}")
                        await channel.send(f"{emoji} This channel's chat cooldown has been set to {cooldown} seconds due to recent message activity.")
                    except discord.Forbidden:
                        logger.warning(f"Unable to change chat slowmode for {channel}, disconnecting relay.")
                        await channel.send("⚠️ I don't have the permissions to change the chat cooldown speed. This permission is required for the relay connection. Disconnecting the channel from the relay.")
                        fake_ctx = await self.bot.get_context(channel.last_message)  # creating a fake context
                        await self.disconnect_channel.invoke(fake_ctx, channel=channel)
                                                                                                        
    @tasks.loop(minutes=1)
    async def reset_message_counters(self):
        self.message_counters.clear()
                            
    @tasks.loop(hours=1)
    async def check_for_reminder(self):
        # Only check if the bot has finished its first iteration after startup
        if self.is_bot_started:
            current_time = datetime.datetime.now()
            for guild_id, channel_id in self.connected_channels:
                # Check if there was activity in the last hour
                last_message_time = self.last_message_times.get(channel_id)
                if last_message_time and (current_time - last_message_time).total_seconds() <= 3600:
                    # Send safety message
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        logger.info(f"Safety message sent to {channel}")
                        await channel.send(self.safety_message)
        
        self.is_bot_started = True        
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if message.channel.id in self.connected_channels:
            if await self.is_blacklisted(message.author.id):
                await message.channel.send(".")
                return
        if (message.guild.id, message.channel.id) in self.connected_channels:
            # Enforce cooldown based on channel's slowmode setting for each user
            channel_id = message.channel.id
            user_id = message.author.id
            now = datetime.datetime.now()
            channel = message.channel

            # Retrieve the current slowmode delay for the channel
            current_slowmode_delay = channel.slowmode_delay

            # Calculate the elapsed time since the last message from this user in this channel
            last_message_time = self.user_last_message_time[channel_id].get(user_id, datetime.datetime.min)
            elapsed_time = (now - last_message_time).total_seconds()

            # Calculate remaining cooldown time
            remaining_cooldown = current_slowmode_delay - elapsed_time

            if elapsed_time < current_slowmode_delay:
                try:
                    # If the message is sent before the cooldown has elapsed, delete the message
                    await message.delete()
                    warning_msg = (f"{message.author.mention}, it looks like you have permissions to bypass the cooldown on this server. "
                                "Unfortunately, we must limit you as well to allow the bot to avoid rate limits. "
                                f"You can send another message in {int(remaining_cooldown)} seconds.")
                    await message.channel.send(warning_msg, delete_after=10)
                    return  # Stop processing this message
                except discord.Forbidden:
                    logger.error("I don't have permission to delete messages in this channel.")
                except discord.HTTPException as e:
                    logger.error(f"An error occurred while trying to delete a message: {e}")
            else:
                # Update the last message time for this user in this channel
                self.user_last_message_time[channel_id][user_id] = now

            # Check the message content before proceeding
            if not await self.check_message_content(message):
                return  # Skip relaying this message

            # Increment message counter for dynamic slowmode
            self.message_counters[message.channel.id] += 1

            # Record the timestamp of the message for messages per minute calculation
            self.message_timestamps[message.channel.id].append(datetime.datetime.now())

            # Remove messages older than 15 minutes for efficient memory usage
            fifteen_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=15)
            self.message_timestamps[message.channel.id] = [timestamp for timestamp in self.message_timestamps[message.channel.id] if timestamp > fifteen_mins_ago]

            # Update last message time for safety reminders
            self.last_message_times[message.channel.id] = datetime.datetime.now()
            self.update_last_message_time_in_db(message.channel.id, datetime.datetime.now())

            # Relay message to other connected channels
            for guild_id, channel_id in self.connected_channels:
                if guild_id != message.guild.id or channel_id != message.channel.id:
                    target_guild = self.bot.get_guild(guild_id)
                    if target_guild:
                        target_channel = target_guild.get_channel(channel_id)
                        if target_channel:
                            await target_channel.send(f"**{message.author.display_name}:** {message.content}")

                        
    @commands.command(usage="!connect_channel")
    @commands.has_permissions(administrator=True)
    async def connect_channel(self, ctx, channel: discord.TextChannel=None):
        """Connect a the current channel to the relay channels. (It's like a large groupchat across servers!)"""
        if not channel:
            channel = ctx.channel
    
        # 1. Send a confirmation message
        confirm_message = await ctx.send(f"Are you sure you want to connect {channel.mention}?\n"
                                         "Any messages sent will be sent to other channels as well "
                                         "as other messages sent from other Servers connected.")
        
        # 2. Add green and red emoji reactions to the message
        green_check = "✅"
        red_cross = "❌"
        await confirm_message.add_reaction(green_check)
        await confirm_message.add_reaction(red_cross)
    
        # 3. Use `wait_for` to listen for the author's reaction
        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [green_check, red_cross] and reaction.message.id == confirm_message.id
    
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)  # wait for 60 seconds
            if str(reaction.emoji) == green_check:
                # 4. If author reacts with the green emoji, proceed with channel connection
                self.connected_channels.add((ctx.guild.id, channel.id))
                self.add_channel_to_db(ctx.guild.id, channel.id)
                await ctx.send(self.safety_message)
                await ctx.send(f"Connected {channel.mention} for relaying messages. This channel is now connected to external channels! To disconnect channel, use `disconnect_channel`")
            else:
                await ctx.send("Channel connection cancelled.")
        except asyncio.TimeoutError:
            await ctx.send("Channel connection request timed out.")
        
    @commands.command(usage="!disconnect_channel")
    @commands.has_permissions(administrator=True)
    async def disconnect_channel(self, ctx, channel: discord.TextChannel=None):
        """Disconnect the channel connected to the relay channels."""
        if not channel:
            channel = ctx.channel
        self.connected_channels.discard((ctx.guild.id, channel.id))
        self.remove_channel_from_db(ctx.guild.id, channel.id)
        await ctx.send(f"Disconnected {channel.mention} from relaying messages.")

    async def check_message_content(self, message):
        """
        Check if the message contains any banned words or links, and handle accordingly.
        
        :param message: The Discord message object to check.
        :return: True if the message is okay to be relayed, False otherwise.
        """
        block_links = True

        # Check for links
        if block_links and ("http://" in message.content or "https://" in message.content or "www." in message.content):
            logger.info("Message blocked due to containing a link.")
            try:
                # Attempt to delete the original message
                await message.delete()
                # Send a warning message to the channel and delete it after 30 seconds
                warning_message = await message.channel.send(
                    f"{message.author.mention}, your message was deleted because it contained a link. "
                    "Sharing links in this channel is not allowed.", 
                    delete_after=30
                )
            except discord.Forbidden:
                logger.error("I don't have permission to delete messages or send messages in this channel.")
                await message.channel.send("Unable to delete messages. Please check perms.\n Message was not relayed as sharing links in this channel is not allowed.")
            except discord.HTTPException as e:
                logger.error(f"An error occurred while trying to delete a message or send a warning: {e}")
            return False  # Indicate the message should not be relayed

        return True  # Message is okay to be relayed
    
async def setup(bot):
    await bot.add_cog(ChannelRelay(bot))
