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
