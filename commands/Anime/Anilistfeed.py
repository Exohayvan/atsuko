import discord
from discord.ext import commands, tasks
import sqlite3
import requests
import asyncio
import os
import logging

logger = logging.getLogger('AnilistFeed.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/AnilistFeed.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("AnilistFeed Cog Loaded. Logging started...")

class AnilistFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.feed_db_path = 'data/db/anilistfeed.db'
        os.makedirs(os.path.dirname(self.feed_db_path), exist_ok=True)
        self.feed_conn = sqlite3.connect(self.feed_db_path)
        self.feed_c = self.feed_conn.cursor()
        self.create_feed_database()
        self.create_activity_database()
        self.check_anilist_updates.start()

    def create_feed_database(self):
        self.feed_c.execute('''CREATE TABLE IF NOT EXISTS feed_channels
                               (guild_id INTEGER, channel_id INTEGER)''')
        self.feed_conn.commit()

    def create_activity_database(self):
        activity_conn = sqlite3.connect('data/db/anilistactivity.db')
        activity_c = activity_conn.cursor()
        activity_c.execute('''CREATE TABLE IF NOT EXISTS last_activity
                              (user_id INTEGER PRIMARY KEY, last_activity_id INTEGER)''')
        activity_conn.commit()
        activity_conn.close()

    @commands.command()
    async def setanifeed(self, ctx):
        """Sets the channel for AniList feed updates."""
        self.feed_c.execute("INSERT OR REPLACE INTO feed_channels (guild_id, channel_id) VALUES (?, ?)", (ctx.guild.id, ctx.channel.id))
        self.feed_conn.commit()
        await ctx.send(f"AniList feed updates will be posted in this channel.")

    @tasks.loop(seconds=60)
    async def check_anilist_updates(self):
        logger.warning("Checking for updates. Possible high API calls.")
        # Connect to the AniList and activity databases
        anilist_conn = sqlite3.connect('data/db/anilist.db')
        anilist_c = anilist_conn.cursor()
        activity_conn = sqlite3.connect('data/db/anilistactivity.db')
        activity_c = activity_conn.cursor()
    
        # Fetch all users and their AniList usernames
        anilist_c.execute("SELECT id, username FROM usernames")
        users = anilist_c.fetchall()
    
        for user_id, username in users:
            logger.info(f"Fetching latest activity for {username} | {user_id}")
            # Fetch the AniList user ID and their latest activity
            anilist_user_id = self.fetch_anilist_user_id(username)
            if anilist_user_id:
                activity = self.fetch_latest_activity(anilist_user_id)
                if activity:
                    # Check if this activity is already posted
                    logger.info(f"Checking if activity for {username} is new")
                    activity_c.execute("SELECT last_activity_id FROM last_activity WHERE user_id=?", (user_id,))
                    last_activity_id = activity_c.fetchone()
                    if not last_activity_id or last_activity_id[0] != activity['id']:
                        # Post the update to all servers where the user is a member
                        logger.info(f"New Activity for {username} found.")
                        for guild in self.bot.guilds:
                            member = guild.get_member(user_id)
                            if member:
                                self.feed_c.execute("SELECT channel_id FROM feed_channels WHERE guild_id=?", (guild.id,))
                                channel_id = self.feed_c.fetchone()
                                if channel_id:
                                    channel = guild.get_channel(channel_id[0])
                                    if channel:
                                        message = f"{member.mention}, {activity['status']} {activity['media_name']}.\n[View Here]({activity['link']})"
                                        await channel.send(message)
                                        logger.info(f"Update sent to {channel_id}")
                                        await asyncio.sleep(1)
    
                        # Update the last activity ID for the user
                        logger.info(f"Updating last activity ID for {username}")
                        activity_c.execute("INSERT OR REPLACE INTO last_activity (user_id, last_activity_id) VALUES (?, ?)", (user_id, activity['id']))
                        activity_conn.commit()
    
        # Close the database connections
        activity_conn.close()
        anilist_conn.close()
        
    def fetch_anilist_user_id(self, username):
        query = '''
        query ($username: String) {
            User(name: $username) {
                id
            }
        }
        '''
        variables = {'username': username}
        response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})

        if response.status_code == 200:
            data = response.json()
            return data['data']['User']['id']
        else:
            return None

    def fetch_latest_activity(self, anilist_user_id):
        query = '''
        query ($userId: Int) {
          Page(page: 1, perPage: 1) {
            activities(userId: $userId, sort: ID_DESC) {
              ... on ListActivity {
                id
                status
                progress
                media {
                  title {
                    romaji
                    english
                  }
                  siteUrl
                  type # This is added to distinguish between anime and manga
                }
                createdAt
              }
            }
          }
        }
        '''
        variables = {'userId': anilist_user_id}
        response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    
        if response.status_code == 200:
            data = response.json()
            activities = data['data']['Page']['activities']
            if activities:
                activity = activities[0]
                media_type = "Anime" if activity['media']['type'] == 'ANIME' else "Manga"
                return {
                    'id': activity['id'],
                    'status': activity['status'],
                    'media_name': activity['media']['title']['english'] or activity['media']['title']['romaji'],
                    'link': activity['media']['siteUrl'],
                    'media_type': media_type  # Include the type of media in the return data
                }
        return None

    @check_anilist_updates.before_loop
    async def before_check_anilist_updates(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AnilistFeed(bot))
