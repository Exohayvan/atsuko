from discord.ext import commands
import random

class Character:
    def __init__(self, name, race, character_class, level):
        self.name = name
        self.race = race
        self.character_class = character_class
        self.level = level

    def __str__(self):
        return f"Name: {self.name}\nRace: {self.race}\nClass: {self.character_class}\nLevel: {self.level}"

class DND(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = {}  # Store characters as {user_id: Character}

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

    @commands.command()
    async def create_character(self, ctx, name, race, character_class, level=1):
        """Creates a D&D character for the user."""
        user_id = ctx.author.id
        if user_id in self.characters:
            await ctx.send("You already have a character!")
            return

        character = Character(name, race, character_class, level)
        self.characters[user_id] = character
        await ctx.send(f"Character '{name}' created for user {ctx.author.mention}!")

    @commands.command()
    async def show_character(self, ctx):
        """Displays the character of the user."""
        user_id = ctx.author.id
        character = self.characters.get(user_id)
        if character:
            await ctx.send(f"User {ctx.author.mention}'s character:\n{character}")
        else:
            await ctx.send("You haven't created a character yet!")

async def setup(bot):
    await bot.add_cog(DND(bot))
