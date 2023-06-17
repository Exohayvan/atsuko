from discord.ext import commands
import random

class DND(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def attack(self, ctx):
        """Simulates an attack in D&D."""
        attack_roll = random.randint(1, 20)
        await ctx.send(f"You rolled {attack_roll} for your attack!")

    @commands.command()
    async def spell(self, ctx):
        """Casts a spell in D&D."""
        spells = ['Fireball', 'Magic Missile', 'Healing Touch']
        spell_cast = random.choice(spells)
        await ctx.send(f"You cast {spell_cast}!")

async def setup(bot):
    await bot.add_cog(DND(bot))
