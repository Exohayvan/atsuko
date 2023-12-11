import discord
from discord.ext import commands
import sqlite3
import requests
import os

class AniList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'data/db/anilist.db'
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)  # Open connection
        self.c = self.conn.cursor()  # Create a cursor
        self.create_database()

    def create_database(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS usernames
                      (id INTEGER PRIMARY KEY, username TEXT)''')
        self.conn.commit()

    def cog_unload(self):
        """Closes the database connection when the cog is unloaded."""
        self.conn.close()  # Close the connection when the cog is unloaded

    @commands.group()
    async def anilist(self, ctx):
        """AniList commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid AniList command. Use `!anilist help` for more information.")

    @anilist.command()
    async def watching(self, ctx, user: discord.Member = None):
        """Fetches the user's or mentioned user's watching list from AniList."""
        if user is None:
            user = ctx.author

        self.c.execute("SELECT username FROM usernames WHERE id=?", (user.id,))
        result = self.c.fetchone()

        if result is not None:
            username = result[0]
        else:
            await ctx.send(f"{user.mention} has not set their AniList username.")
            return

        query = '''
        query ($username: String) {
            MediaListCollection(userName: $username, type: ANIME, status: CURRENT) {
                lists {
                    entries {
                        media {
                            title {
                                english
                                romaji
                            }
                        }
                    }
                }
            }
        }
        '''
        variables = {'username': username}

        response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})

        if response.status_code == 200:
            data = response.json()
            watching_list = data['data']['MediaListCollection']['lists'][0]['entries']

            embed = discord.Embed(title=f"{user}'s Watching List", color=discord.Color.blue())

            for entry in watching_list:
                media = entry['media']
                title = media['title']['english'] or media['title']['romaji']
                embed.add_field(name="\u200B", value=f"• {title}", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to fetch watching list.")

    @anilist.command()
    async def help(self, ctx):
        """Displays Help infor with command"""
        await ctx.send("Looking for help? First do you have an AniList.co account? Once you have one if you dont already. Use `anilist set <username>` to set your account. Then you can use `anilist stats`")

    @anilist.command()
    async def set(self, ctx, username):
        """Sets the user's AniList username."""
        self.c.execute("INSERT OR REPLACE INTO usernames (id, username) VALUES (?, ?)", (ctx.author.id, username))
        self.conn.commit()
        await ctx.send("AniList username set successfully.")

    @anilist.command()
    async def stats(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
    
        self.c.execute("SELECT username FROM usernames WHERE id=?", (user.id,))
        result = self.c.fetchone()
    
        if result is not None:
            username = result[0]
        else:
            await ctx.send(f"{user.mention} has not set their AniList username.")
            return
    
        # Fetch the user's ID from the username
        user_query = '''
        query ($username: String) {
            User(name: $username) {
                id
            }
        }
        '''
        user_variables = {'username': username}
        user_response = requests.post('https://graphql.anilist.co', json={'query': user_query, 'variables': user_variables})
        user_data = user_response.json()
        user_id = user_data['data']['User']['id']
    
        # Fetch the entire anime list for the user
        list_query = '''
        query ($userId: Int) {
            MediaListCollection(userId: $userId, type: ANIME) {
                lists {
                    name
                    entries {
                        status
                    }
                }
            }
        }
        '''
        list_variables = {'userId': user_id}
        list_response = requests.post('https://graphql.anilist.co', json={'query': list_query, 'variables': list_variables})
    
        if list_response.status_code != 200:
            await ctx.send(f"Failed to fetch anime stats. API Response: {list_response.content}")
            return
    
        data = list_response.json()
        lists = data['data']['MediaListCollection']['lists']
        watching_count = sum(1 for lst in lists for entry in lst['entries'] if entry['status'] == 'CURRENT')
        completed_count = sum(1 for lst in lists for entry in lst['entries'] if entry['status'] == 'COMPLETED')
        planning_count = sum(1 for lst in lists for entry in lst['entries'] if entry['status'] == 'PLANNING')
    
        # Fetch additional anime statistics (like episodes watched)
        anime_stats_query = '''
        query ($username: String) {
          User(name: $username) {
            statistics {
              anime {
                episodesWatched
                minutesWatched
              }
            }
          }
        }
        '''
        anime_stats_variables = {'username': username}
        anime_stats_response = requests.post('https://graphql.anilist.co', json={'query': anime_stats_query, 'variables': anime_stats_variables})
    
        if anime_stats_response.status_code != 200:
            await ctx.send("Failed to fetch anime statistics.")
            return
    
        anime_stats_data = anime_stats_response.json()
        episodes = anime_stats_data['data']['User']['statistics']['anime']['episodesWatched']
        total_minutes = anime_stats_data['data']['User']['statistics']['anime']['minutesWatched']
        days = total_minutes // (24 * 60)
        hours = (total_minutes % (24 * 60)) // 60
        minutes = total_minutes % 60
        time_watched_str = f"{days} days, {hours} hours, {minutes} minutes"
    
        # Fetch the entire manga list for the user
        manga_list_query = '''
        query ($userId: Int) {
            MediaListCollection(userId: $userId, type: MANGA) {
                lists {
                    name
                    entries {
                        status
                        progress
                    }
                }
            }
        }
        '''
        manga_list_variables = {'userId': user_id}
        manga_list_response = requests.post('https://graphql.anilist.co', json={'query': manga_list_query, 'variables': manga_list_variables})
    
        if manga_list_response.status_code != 200:
            await ctx.send(f"Failed to fetch manga stats. API Response: {manga_list_response.content}")
            return
    
        manga_data = manga_list_response.json()
        manga_lists = manga_data['data']['MediaListCollection']['lists']
        manga_reading_count = sum(1 for lst in manga_lists for entry in lst['entries'] if entry['status'] == 'CURRENT')
        manga_read_count = sum(1 for lst in manga_lists for entry in lst['entries'] if entry['status'] == 'COMPLETED')
        manga_planned_count = sum(1 for lst in manga_lists for entry in lst['entries'] if entry['status'] == 'PLANNING')
        manga_chapters_read = sum(entry['progress'] for lst in manga_lists for entry in lst['entries'])
    
        # Calculate time spent reading manga
        total_manga_minutes = manga_chapters_read * 9
        manga_days = total_manga_minutes // (24 * 60)
        manga_hours = (total_manga_minutes % (24 * 60)) // 60
        manga_minutes = total_manga_minutes % 60
        time_read_str = f"{manga_days} days, {manga_hours} hours, {manga_minutes} minutes"
    
        # Add both anime and manga stats to the embed
        embed = discord.Embed(title=f"{user}'s AniList Stats", color=discord.Color.blue())
        embed.add_field(name="Animes Watching", value=watching_count, inline=True)
        embed.add_field(name="Animes Watched", value=completed_count, inline=True)
        embed.add_field(name="Animes Planned", value=planning_count, inline=True)
        embed.add_field(name="Episodes Watched", value=episodes, inline=True)
        embed.add_field(name="Time Spent Watching Anime", value=time_watched_str, inline=True)
        embed.add_field(name="Mangas Reading", value=manga_reading_count, inline=True)
        embed.add_field(name="Mangas Read", value=manga_read_count, inline=True)
        embed.add_field(name="Mangas Planned", value=manga_planned_count, inline=True)
        embed.add_field(name="Chapters Read", value=manga_chapters_read, inline=True)
        embed.add_field(name="Time Spent Reading Manga", value=time_read_str, inline=True)
    
        await ctx.send(embed=embed)
                                                    
async def setup(bot):
    await bot.add_cog(AniList(bot))
