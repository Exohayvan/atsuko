import discord
from discord.ext import commands
import json
import re
import shlex

class HyperBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="!hyper <usage>")
    async def hyper(self, ctx):
        """This is the hyper command."""
        await ctx.message.delete()

        content = ctx.message.content
        content = content.replace("!hyper ", "")

        title = None
        match = re.search(r'"([^"]*)"', content)
        if match:
            title = match.group(1)
            content = content.replace(f'"{title}"', '')

        args = shlex.split(content)
        if len(args) % 3 != 0:
            await ctx.send("Error: Invalid number of arguments. Please provide sets of names, links, and descriptions.")
            return

        triples = [args[n:n+3] for n in range(0, len(args), 3)]
        links = "\n".join([f"[{triple[0]}]({triple[1]})\n*{triple[2]}*\n" for triple in triples])

        embed = discord.Embed()
        if title:
            embed.title = title
        embed.description = links
        await ctx.send(embed=embed)

    @commands.command(usage="!embed <message>")
    async def embed(self, ctx):
        """This is the embed command."""
        # remove the "!embed " part from the message
        content = ctx.message.content.replace("!embed ", "")
        
        # create an embed with the remaining content
        embed = discord.Embed(description=content)
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(HyperBot(bot))
