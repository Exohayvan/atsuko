import requests
import discord
from discord.ext import commands

class AniList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def watching(self, ctx, username):
        """Fetches the user's watching list from AniList."""
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
            
            embed = discord.Embed(title=f"{username}'s Watching List", color=discord.Color.blue())
            
            for entry in watching_list:
                media = entry['media']
                title = media['title']['english'] or media['title']['romaji']
                embed.add_field(value=title, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to fetch watching list.")

async def setup(bot):
    await bot.add_cog(AniList(bot))