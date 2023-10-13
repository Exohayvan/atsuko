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
    
        # First, get the user's ID from the username.
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
    
        # Fetch the entire anime list for the user.
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
            await ctx.send(f"Failed to fetch stats. API Response: {list_response.content}")
            return
    
        data = list_response.json()
        lists = data['data']['MediaListCollection']['lists']
        watching_count = sum(1 for lst in lists for entry in lst['entries'] if entry['status'] == 'CURRENT')
        completed_count = sum(1 for lst in lists for entry in lst['entries'] if entry['status'] == 'COMPLETED')
        planning_count = sum(1 for lst in lists for entry in lst['entries'] if entry['status'] == 'PLANNING')
    
        # Fetch watched statistics
        watched_query = '''
        query ($username: String) {
          User(name: $username) {
            statistics {
              anime {
                minutesWatched
                episodesWatched
              }
            }
          }
        }
        '''
        watched_variables = {'username': username}
        watched_response = requests.post('https://graphql.anilist.co', json={'query': watched_query, 'variables': watched_variables})
    
        if watched_response.status_code != 200:
            await ctx.send(f"Failed to fetch watched statistics. API Response: {watched_response.content}")
            return
    
        watched_data = watched_response.json()
        total_minutes = watched_data['data']['User']['statistics']['anime']['minutesWatched']
        episodes = watched_data['data']['User']['statistics']['anime']['episodesWatched']
        
        days = total_minutes // (24 * 60)
        hours = (total_minutes % (24 * 60)) // 60
        minutes = total_minutes % 60
        time_watched_str = f"{days} days, {hours} hours, {minutes} minutes"
    
        # Fetch top 3 genres
        genre_query = '''
        query ($username: String) {
          User(name: $username) {
            statistics {
              anime {
                genres(limit: 3) {
                  genre
                }
              }
            }
          }
        }
        '''
        genre_variables = {'username': username}
        genre_response = requests.post('https://graphql.anilist.co', json={'query': genre_query, 'variables': genre_variables})
    
        if genre_response.status_code != 200:
            await ctx.send(f"Failed to fetch top genres. API Response: {genre_response.content}")
            return
    
        genre_data = genre_response.json()
        top_genres = ", ".join([genre['genre'] for genre in genre_data['data']['User']['statistics']['anime']['genres']])
    
        embed = discord.Embed(title=f"{user}'s AniList Stats", color=discord.Color.blue())
        embed.add_field(name="Animes Watching", value=watching_count, inline=True)
        embed.add_field(name="Animes Watched", value=completed_count, inline=True)
        embed.add_field(name="Animes Planned", value=planning_count, inline=True)
        embed.add_field(name="Time Watched", value=time_watched_str, inline=True)
        embed.add_field(name="Episodes Watched", value=episodes, inline=True)
        embed.add_field(name="Top 3 Genres", value=top_genres, inline=True)
    
        await ctx.send(embed=embed)
                                                    
async def setup(bot):
    await bot.add_cog(AniList(bot))