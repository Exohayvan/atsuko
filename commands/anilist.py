import discord
from discord.ext import commands
import sqlite3
import requests
import os

class AniList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = '.data/db/anilist.db'
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
    async def set(self, ctx, username):
        """Sets the user's AniList username."""
        self.c.execute("INSERT OR REPLACE INTO usernames (id, username) VALUES (?, ?)", (ctx.author.id, username))
        self.conn.commit()
        await ctx.send("AniList username set successfully.")

    @anilist.command()
    async def stats(self, ctx, user: discord.Member = None):
        """Fetches the user's or mentioned user's stats from AniList."""
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
            User(name: $username) {
                stats {
                    anime {
                        episodesWatched
                        minutesWatched
                        statuses {
                            watching
                            completed
                            planning
                        }
                        genres(limit: 3)
                        tags(limit: 3)
                        staff(limit: 3) {
                            id
                            name {
                                full
                            }
                        }
                        studios(limit: 3) {
                            id
                            name
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
            anime_stats = data['data']['User']['stats']['anime']

            embed = discord.Embed(title=f"{user}'s AniList Stats", color=discord.Color.blue())

            # Anime Statuses
            embed.add_field(name="Animes Watching", value=anime_stats['statuses']['watching'], inline=True)
            embed.add_field(name="Animes Watched", value=anime_stats['statuses']['completed'], inline=True)
            embed.add_field(name="Animes Planned", value=anime_stats['statuses']['planning'], inline=True)

            # Episodes and Days
            embed.add_field(name="Episodes Watched", value=anime_stats['episodesWatched'], inline=True)
            embed.add_field(name="Days Watched", value=anime_stats['minutesWatched'] / 1440, inline=True) # 1440 minutes = 1 day
            # Note: Days Planned is not directly available from AniList's API without more complex querying.

            # Genres, Tags, Voice Actors, Studios
            embed.add_field(name="Top 3 Genres", value=", ".join(anime_stats['genres']), inline=True)
            embed.add_field(name="Top 3 Tags", value=", ".join([tag['name'] for tag in anime_stats['tags']]), inline=True)
            embed.add_field(name="Top 3 Voice Actors", value=", ".join([staff['name']['full'] for staff in anime_stats['staff']]), inline=True)
            embed.add_field(name="Top 3 Studios", value=", ".join([studio['name'] for studio in anime_stats['studios']]), inline=True)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to fetch stats.")
            
async def setup(bot):
    await bot.add_cog(AniList(bot))