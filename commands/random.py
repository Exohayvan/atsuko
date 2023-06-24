from discord.ext import commands
import string
import random
import aiohttp
import discord

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def fetch(self, url):
        try:
            async with self.session.get(url) as response:
                return response.status
        except Exception:
            return None

    @commands.group(invoke_without_command=True)
    async def random(self, ctx):
        """Shows a help message for the random group command."""
        await ctx.send("Use !random with one of the following: website, reddit, saying")

    @random.command()
    async def website(self, ctx):
        """Returns a random website."""

        websites_checked = 0
        loading_message = await ctx.send(embed=discord.Embed(
            title="Generating a random website…",
            description=f"Websites checked: {websites_checked}"
        ))

        while True:
            random_url = f"https://www.{''.join(random.choices(string.ascii_lowercase, k=10))}.com"
            status = await self.fetch(random_url)
            websites_checked += 1

            if websites_checked % 20 == 0:
                await loading_message.edit(embed=discord.Embed(
                    title="Generating a random website…",
                    description=f"Websites checked: {websites_checked}"
                ))

            if status == 200:
                await loading_message.edit(embed=discord.Embed(
                    title="Random Website", 
                    description=random_url,
                    footer="This is a randomly generated website. Please browse at your own risk."
                ))
                break

    @random.command()
    async def reddit(self, ctx):
        """Returns a link to a random subreddit."""
        result = "https://www.reddit.com/r/random"

        embed = discord.Embed(title="Random Subreddit", description=f"{result}")
        embed.set_footer(text="This link directs to a random subreddit. The content is randomly generated. Please browse at your own risk. Refresh the page to generate a new subreddit.")

        await ctx.send(embed=embed)

    @random.command()
    async def saying(self, ctx):
        """Returns a random saying."""
        response = requests.get("https://api.quotable.io/random")
    
        if response.status_code == 200:
            try:
                data = response.json()
                quote = data['content']
                author = data['author']

                embed = discord.Embed(title="Random Saying", description=f'"{quote}" - {author}')
                embed.set_footer(text="This is a randomly generated saying. Interpret at your own risk.")
                await ctx.send(embed=embed)
            except json.JSONDecodeError:
                await ctx.send("Sorry, the quote API did not return valid JSON.")
        else:
            await ctx.send("Sorry, I couldn't fetch a saying right now.")

async def setup(bot):
    await bot.add_cog(Random(bot))
