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
                mediaListCollection(type: ANIME) {
                    lists {
                        name
                        entries {
                            status
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
            
            # Check if the 'data' key is in the response and if 'User' is None
            if 'data' in data and data['data']['User'] is None:
                await ctx.send(f"No AniList data found for the username {username}.")
                return
    
            lists = data['data']['User']['mediaListCollection']['lists']
            
            watching_count = sum(1 for entry in lists if entry['status'] == 'WATCHING')
            completed_count = sum(1 for entry in lists if entry['status'] == 'COMPLETED')
            planning_count = sum(1 for entry in lists if entry['status'] == 'PLANNING')
    
            embed = discord.Embed(title=f"{user}'s AniList Stats", color=discord.Color.blue())
            embed.add_field(name="Animes Watching", value=watching_count, inline=True)
            embed.add_field(name="Animes Watched", value=completed_count, inline=True)
            embed.add_field(name="Animes Planned", value=planning_count, inline=True)
    
            await ctx.send(embed=embed)
        else:
            # Printing the response content for debugging
            await ctx.send(f"Failed to fetch stats. API Response: {response.content}")
                                        
async def setup(bot):
    await bot.add_cog(AniList(bot))