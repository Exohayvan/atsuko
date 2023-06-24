from discord.ext import commands
import random
import requests
import discord

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def random(self, ctx):
        """Shows a help message for the random group command."""
        await ctx.send("Use !random with one of the following: website, reddit, saying")

    @random.command()
    async def website(self, ctx):
        """Returns a random website."""
        # you need a list of websites to choose from
        websites = ['http://example1.com', 'http://example2.com', 'http://example3.com']
        result = random.choice(websites)

        embed = discord.Embed(title="Random Website", description=result)
        embed.set_footer(text="This is a randomly generated website. Please browse at your own risk.")

        await ctx.send(embed=embed)

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
        response = requests.get("https://quote-garden.herokuapp.com/api/v3/quotes/random")
        data = response.json()

        if response.status_code == 200 and data.get('data'):
            result = data['data'][0]['quoteText']
            author = data['data'][0]['quoteAuthor']

            embed = discord.Embed(title="Random Saying", description=f'"{result}" - {author}')
            embed.set_footer(text="This is a randomly generated saying. Interpret at your own risk.")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, I couldn't fetch a saying right now.")

async def setup(bot):
    await bot.add_cog(Random(bot))
