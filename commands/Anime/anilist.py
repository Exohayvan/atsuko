import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import requests
import aiohttp
import os
import asyncio
import logging

logger = logging.getLogger('AniList.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/AniList.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("AniList Cog Loaded. Logging started...")

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

    #Old needs removed after slash update.
    @commands.group()
    async def anilist(self, ctx):
        """AniList commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid AniList command. Use `!anilist help` for more information.")
            logger.error("Invalid AniList command.")

    
    group = app_commands.Group(name="anilist", description="...")

    @group.command(name="help", description="Display info about how to use this.")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("Looking for help? First do you have an AniList.co account? Once you have one if you dont already. Use `anilist set <username>` to set your account. Then you can use `anilist stats`")

    @group.command(name="watching", description="Fetches the user's or mentioned user's watching list from AniList.")
    async def watching(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            user = interaction.user

        self.c.execute("SELECT username FROM usernames WHERE id=?", (user.id,))
        result = self.c.fetchone()

        if result is not None:
            username = result[0]
        else:
            await interaction.response.send_message(f"{user.mention} has not set their AniList username.")
            logger.error("User has not set their AniList username.")
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

        response = await asyncio.to_thread(requests.post, 'https://graphql.anilist.co', json={'query': query, 'variables': variables})

        if response.status_code == 200:
            data = response.json()
            watching_list = data['data']['MediaListCollection']['lists'][0]['entries']

            embed = discord.Embed(title=f"{user}'s Watching List", color=discord.Color.blue())

            for entry in watching_list:
                media = entry['media']
                title = media['title']['english'] or media['title']['romaji']
                embed.add_field(name="\u200B", value=f"• {title}", inline=False)

            await interaction.response.send_message(embed=embed)
            logger.info(f"Info about user '{username}' sent.")
        else:
            await interaction.response.send_message("Failed to fetch watching list.")
            logger.error("Failed to fetch watching list.")

    @group.command(name="set", description="Sets your AniList username.")
    @app_commands.describe(username="Your AniList username")
    async def set_username(self, interaction: discord.Interaction, username: str):
        user_id = interaction.user.id
            
        self.c.execute("INSERT OR REPLACE INTO usernames (id, username) VALUES (?, ?)", (user_id, username))
        self.conn.commit()
            
        await interaction.response.send_message("AniList username set successfully.")
        logger.info(f"{user_id} set username to {username}")

    @group.command(name="stats", description="Fetches the user's or mentioned user's stats from AniList.")
    async def stats(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            user = interaction.user
        
        await interaction.response.defer()
        
        self.c.execute("SELECT username FROM usernames WHERE id=?", (user.id,))
        result = self.c.fetchone()
    
        if result is not None:
            username = result[0]
        else:
            await interaction.followup.send(f"{user.mention} has not set their AniList username.")
            logger.error("User has not set their AniList username.")
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
            await interaction.followup.send(f"Failed to fetch anime stats. API Response: {list_response.content}")
            logger.error(f"Failed to fetch anime stats. API Response: {list_response.content}")
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
            await interaction.followup.send("Failed to fetch anime statistics.")
            logger.error("Failed to fetch anime statistics.")
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
            await interaction.followup.send(f"Failed to fetch manga stats. API Response: {manga_list_response.content}")
            return
    
        manga_data = manga_list_response.json()
        manga_lists = manga_data['data']['MediaListCollection']['lists']
        manga_reading_count = sum(1 for lst in manga_lists for entry in lst['entries'] if entry['status'] == 'CURRENT')
        manga_read_count = sum(1 for lst in manga_lists for entry in lst['entries'] if entry['status'] == 'COMPLETED')
        manga_planned_count = sum(1 for lst in manga_lists for entry in lst['entries'] if entry['status'] == 'PLANNING')
        manga_chapters_read = sum(entry['progress'] for lst in manga_lists for entry in lst['entries'])
    
        # Calculate time spent reading manga
        total_manga_minutes = manga_chapters_read * 11
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
        
        await interaction.followup.send(embed=embed)

    @anilist.command()
    async def leaderboard(self, ctx):
        # Fetch all users from the database
        self.c.execute("SELECT id, username FROM usernames")
        users = self.c.fetchall()
    
        # Calculate the estimated time
        estimated_time_seconds = len(users) * 4
        estimated_time_message = f"Checking Users Stats... This could take a moment\nEstimated time: {estimated_time_seconds // 60} minutes {estimated_time_seconds % 60} seconds"
        estimation_message = await ctx.send(estimated_time_message)
        logger.warning(f"Pulling total users in server. High API calls. ETA {estimated_time_seconds // 60} minutes.")
    
        leaderboard_data = []

        logger.info("Checking users.")
        for user_id, username in users:
            # Fetch the Discord member
            member = ctx.guild.get_member(user_id)
            if member is None:
                logger.info(f"{username} not found in server. Continuing.")
                continue  # Skip if the member is not found
            
            logger.info(f"{username} found in server. Checking and calculating total times.")
            # Calculate total time for anime and manga
            anime_time = await self.calculate_total_anime_time(username)
            logger.info(f"{username} total anime time: {anime_time}")
            manga_time = await self.calculate_total_manga_time(username)
            logger.info(f"{username} total manga time: {manga_time}")
            
            # Ensure both times are in minutes and sum them
            total_time = anime_time + manga_time  # This line ensures proper summation

            logger.info(f"Appending {member} to leaderboard with {total_time} total time.")
            leaderboard_data.append((member.mention, total_time))
                
            # Wait for 2 seconds
            logger.info("Waiting 2 seconds to avoid API Limits.")
            await asyncio.sleep(2)
    
        # Sort the data by total time (in minutes) and get top 10
        logger.info("Sorting data.")
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
        logger.info("Sent leaderboard.")

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
        minutes_read = chapters_read * 11
        return minutes_read

    @anilist.command()
    async def compare(self, ctx, category: str, user1: discord.Member, user2: discord.Member):
        """Compares AniList anime lists between two users."""
        if category not in ["all", "planned", "watched", "watching"]:
            await ctx.send("Invalid category. Must be one of 'all', 'planned', 'watched', 'watching'.")
            return

        list1 = await self.fetch_user_list_by_category(user1.id, category)
        list2 = await self.fetch_user_list_by_category(user2.id, category)

        # Find similarities
        similarities = set(list1).intersection(set(list2))

        if similarities:
            anime_list = '\n'.join(similarities)
            message = f"📺 Similar Animes ({category}):\n{anime_list}"
        else:
            message = "No similarities found in the specified category."

        await ctx.send(message)
        
    async def fetch_user_list_by_category(self, user_id, category):
        """Fetches the user's AniList anime list by category."""
        self.c.execute("SELECT username FROM usernames WHERE id=?", (user_id,))
        result = self.c.fetchone()
    
        if result is None:
            # User has not set their AniList username
            return []
    
        username = result[0]
    
        # Define the GraphQL query based on the category
        if category == "all":
            query = '''
            query ($username: String) {
                MediaListCollection(userName: $username, type: ANIME) {
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
        elif category == "planned":
            query = '''
            query ($username: String) {
                MediaListCollection(userName: $username, type: ANIME, status: PLANNING) {
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
        elif category == "watched":
            query = '''
            query ($username: String) {
                MediaListCollection(userName: $username, type: ANIME, status: COMPLETED) {
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
        elif category == "watching":
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
        else:
            # Invalid category
            return []
    
        variables = {'username': username}
    
        response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                # Handle errors
                return []
            anime_list = []
            for lst in data['data']['MediaListCollection']['lists']:
                for entry in lst['entries']:
                    media = entry['media']
                    title = media['title']['english'] or media['title']['romaji']
                    anime_list.append(title)
            return anime_list
        else:
            # Failed to fetch anime list
            return []
        
async def setup(bot):
    await bot.add_cog(AniList(bot))
