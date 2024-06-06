from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="!roll NdN")
    async def roll(self, ctx, dice: str):
        """Rolls a dice with the specified format (e.g., 2d6)."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format must be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await ctx.send(f'You rolled: {result}')

    @commands.command(usage="!coinflip")
    async def coinflip(self, ctx):
        """Flips a coin and shows the result."""
        result = random.choice(['Heads', 'Tails'])
        await ctx.send(f"The coin landed on: {result}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
