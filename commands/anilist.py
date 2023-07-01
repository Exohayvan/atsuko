import requests
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
            anime_titles = [entry['media']['title']['romaji'] for entry in watching_list]
            await ctx.send(f"Currently watching: {', '.join(anime_titles)}")
        else:
            await ctx.send("Failed to fetch watching list.")

async def setup(bot):
    await bot.add_cog(AniList(bot))