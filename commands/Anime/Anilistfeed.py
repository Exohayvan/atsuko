import discord
from discord.ext import commands, tasks
import sqlite3
import requests
import os

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
        self.feed_c.execute("SELECT guild_id, channel_id FROM feed_channels")
        channels = self.feed_c.fetchall()

        anilist_conn = sqlite3.connect('data/db/anilist.db')
        anilist_c = anilist_conn.cursor()

        activity_conn = sqlite3.connect('data/db/anilistactivity.db')
        activity_c = activity_conn.cursor()

        for guild_id, channel_id in channels:
            guild = self.bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(channel_id)
                if channel:
                    anilist_c.execute("SELECT id, username FROM usernames")
                    for user_id, username in anilist_c.fetchall():
                        member = guild.get_member(user_id)
                        if member:
                            anilist_user_id = self.fetch_anilist_user_id(username)
                            if anilist_user_id:
                                activity = self.fetch_latest_activity(anilist_user_id)
                                if activity:
                                    activity_c.execute("SELECT last_activity_id FROM last_activity WHERE user_id=?", (user_id,))
                                    last_activity_id = activity_c.fetchone()
                                    if not last_activity_id or last_activity_id[0] != activity['id']:
                                        message = f"{member.mention}, {activity['status']} {activity['episode_name']}.\n[Watch Here]({activity['link']})"
                                        await channel.send(message)
                                        activity_c.execute("INSERT OR REPLACE INTO last_activity (user_id, last_activity_id) VALUES (?, ?)", (user_id, activity['id']))
                                        activity_conn.commit()

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
            activities(userId: $userId, type: ANIME_LIST, sort: ID_DESC) {
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
                return {
                    'id': activity['id'],
                    'status': activity['status'],
                    'episode_name': activity['media']['title']['english'] or activity['media']['title']['romaji'],
                    'link': activity['media']['siteUrl']
                }
        return None

    @check_anilist_updates.before_loop
    async def before_check_anilist_updates(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AnilistFeed(bot))
