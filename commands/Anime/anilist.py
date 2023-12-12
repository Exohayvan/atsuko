import discord
from discord.ext import commands
import sqlite3
import requests
import os
import asyncio

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
        total_manga_minutes = manga_chapters_read * 13
        manga_days = total_manga_minutes // (24 * 60)
        manga_hours = (total_manga_minutes % (24 * 60)) // 60
        manga_minutes = total_manga_minutes % 60
        time_read_str = f"{manga_days} days, {manga_hours} hours, {manga_minutes} minutes"

        # Calculate total time spent
        total_minutes = total_minutes + total_manga_minutes
        total_days = total_minutes // (24 * 60)
        total_hours = (total_minutes % (24 * 60)) // 60
        total_minutes_remaining = total_minutes % 60
        total_time_spent_str = f"{total_days} days, {total_hours} hours, {total_minutes_remaining} minutes"
    
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
        embed.add_field(name="Total Time Spent Being A Weeb", value=total_time_spent_str, inline=True)
        
        await ctx.send(embed=embed)

    @anilist.command()
    async def leaderboard(self, ctx):
        # Fetch all users from the database
        self.c.execute("SELECT id, username FROM usernames")
        users = self.c.fetchall()
    
        # Calculate the estimated time
        estimated_time_seconds = len(users) * 4
        estimated_time_message = f"Checking Users Stats... This could take a moment\nEstimated time: {estimated_time_seconds // 60} minutes {estimated_time_seconds % 60} seconds"
        estimation_message = await ctx.send(estimated_time_message)
    
        leaderboard_data = []
    
        for user_id, username in users:
            # Fetch the Discord member
            member = ctx.guild.get_member(user_id)
            if member is None:
                continue  # Skip if the member is not found
    
            # Calculate total time for anime and manga
            anime_time = await self.calculate_total_anime_time(username)
            manga_time = await self.calculate_total_manga_time(username)
            total_time = anime_time + manga_time
    
            leaderboard_data.append((member.mention, total_time))
    
            # Wait for 2 seconds
            await asyncio.sleep(2)
    
        # Sort the data by total time (in minutes) and get top 10
        leaderboard_sorted = sorted(leaderboard_data, key=lambda x: x[1], reverse=True)[:10]
    
        # Create an embed for the leaderboard
        embed = discord.Embed(title="Top 10 Weebs Leaderboard", color=discord.Color.blue())
        for rank, (user_mention, total_time) in enumerate(leaderboard_sorted, start=1):
            formatted_time = self.format_time(total_time)
            embed.add_field(name=f"#{rank} {user_mention}", value=f"Total Time: {formatted_time}", inline=False)
    
        # Delete the estimation message
        await estimation_message.delete()
    
        # Send the leaderboard embed
        await ctx.send(embed=embed)

    def format_time(self, total_minutes):
        days = total_minutes // (24 * 60)
        hours = (total_minutes % (24 * 60)) // 60
        minutes = total_minutes % 60
        return f"{days}d {hours}h {minutes}m"
    
    async def calculate_total_anime_time(self, username):
        # Fetch anime statistics
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
            # Handle errors appropriately
            return 0
        anime_stats_data = anime_stats_response.json()
        minutes_watched = anime_stats_data['data']['User']['statistics']['anime']['minutesWatched']
        return minutes_watched
                                                    
    async def calculate_total_manga_time(self, username):
        # Fetch manga statistics
        manga_stats_query = '''
        query ($username: String) {
          User(name: $username) {
            statistics {
              manga {
                chaptersRead
              }
            }
          }
        }
        '''
        manga_stats_variables = {'username': username}
        manga_stats_response = requests.post('https://graphql.anilist.co', json={'query': manga_stats_query, 'variables': manga_stats_variables})
    
        if manga_stats_response.status_code != 200:
            # Handle errors appropriately
            return 0
        manga_stats_data = manga_stats_response.json()
        chapters_read = manga_stats_data['data']['User']['statistics']['manga']['chaptersRead']
        # Assuming an average of 10 minutes per chapter (this can be adjusted)
        minutes_read = chapters_read * 13
        return minutes_read
        
async def setup(bot):
    await bot.add_cog(AniList(bot))
