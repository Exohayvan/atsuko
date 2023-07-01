import requests
from discord.ext import commands

class AniList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def watching(self, ctx, username):
        """Fetches the user's watching list from AniList."""
        # Make a request to the AniList API
        response = requests.get(f"https://api.anilist.co/user/{username}/animelist")
        
        if response.status_code == 200:
            watching_list = response.json()["lists"]["watching"]
            anime_titles = [anime["anime"]["title"] for anime in watching_list]
            await ctx.send(f"Currently watching: {', '.join(anime_titles)}")
        else:
            await ctx.send("Failed to fetch watching list.")

async def setup(bot):
    await bot.add_cog(AniList(bot))
